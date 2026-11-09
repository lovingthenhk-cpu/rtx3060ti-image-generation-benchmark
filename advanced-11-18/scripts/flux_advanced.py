import json,time,urllib.request,urllib.parse,traceback
from pathlib import Path
from PIL import Image,ImageDraw
out=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
jobs=json.load(open(out/'prompts.json'))['items']
port=int(Path('/workspace/flux2-port.txt').read_text().strip())
base='http://127.0.0.1:'+str(port)
def get(path,timeout=40):
 with urllib.request.urlopen(base+path,timeout=timeout) as f:return json.load(f)
def post(obj):
 req=urllib.request.Request(base+'/prompt',json.dumps({'prompt':obj,'client_id':'rtx3060ti-benchmark'}).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as f:return json.load(f)
for i in range(120):
 try:
  obj=get('/object_info',timeout=4);print('SERVER_READY',len(obj),flush=True);break
 except Exception:time.sleep(3)
else:raise RuntimeError('ComfyUI server did not respond')
results=[]
for entry in jobs:
 lv=entry['level'];name=entry['name'];seed=30602026+lv*73
 w=640 if entry['width']>640 else 512
 h=640 if entry['height']>640 else 512
 prompt='A high-quality realistic detailed illustration, coherent perspective. '+entry['prompt']+' Obey all object counts and spatial positions accurately. No letters or captions.'
 nodes={
 '1':{'class_type':'UNETLoader','inputs':{'unet_name':'flux-2-klein-4b-fp8.safetensors','weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_4b_fp4_flux2.safetensors','type':'flux2','device':'default'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':'flux2-vae.safetensors'}},
 '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},
 '5':{'class_type':'ConditioningZeroOut','inputs':{'conditioning':['4',0]}},
 '6':{'class_type':'CFGGuider','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'cfg':1.0}},
 '7':{'class_type':'RandomNoise','inputs':{'noise_seed':seed}},
 '8':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},
 '9':{'class_type':'Flux2Scheduler','inputs':{'steps':4,'width':w,'height':h}},
 '10':{'class_type':'EmptyFlux2LatentImage','inputs':{'width':w,'height':h,'batch_size':1}},
 '11':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['7',0],'guider':['6',0],'sampler':['8',0],'sigmas':['9',0],'latent_image':['10',0]}},
 '12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['3',0]}},
 '13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':'benchmark_flux2'}}
 }
 t=time.time()
 rec={'level':lv,'name':name,'prompt':prompt,'seed':seed,'steps':4,'cfg':1.0,'width':w,'height':h,'status':'waiting','filename':f'lv{lv:02d}_flux2.png'}
 try:
  response=post(nodes)
  pid=response.get('prompt_id')
  if not pid:raise RuntimeError('No prompt_id: '+str(response))
  rec['prompt_id']=pid
  for k in range(260):
   time.sleep(3)
   history=get('/history/'+pid)
   if pid not in history:continue
   item=history[pid]
   if item.get('status',{}).get('status_str')=='error':raise RuntimeError(str(item.get('status'))[:600])
   images=item.get('outputs',{}).get('13',{}).get('images',[])
   if images:
    img=images[0]
    uri='/view?filename='+urllib.parse.quote(img['filename'])+'&type=output'
    with urllib.request.urlopen(base+uri,timeout=45) as f:(out/rec['filename']).write_bytes(f.read())
    rec['status']='ok'
    break
  if rec['status']!='ok':raise RuntimeError('Timeout')
 except Exception as ex:
  rec['status']='failed';rec['error']=str(ex)
 rec['seconds']=round(time.time()-t,2)
 results.append(rec)
 (out/'flux2.json').write_text(json.dumps({'model':'FLUX.2 [klein] 4B FP8, Qwen 4B FP4','items':results},ensure_ascii=False,indent=2))
 print('FLUX',lv,rec['status'],rec['seconds'],'seconds',rec.get('error',''),flush=True)
sheet=Image.new('RGB',(470*5,480*2),'white')
for idx,rec in enumerate(results):
 if rec['status']!='ok':continue
 im=Image.open(out/rec['filename']).convert('RGB');im.thumbnail((448,448))
 tile=Image.new('RGB',(470,480),'white');tile.paste(im,((470-im.width)//2,(448-im.height)//2))
 ImageDraw.Draw(tile).text((14,453),f"Lv{rec['level']}: {rec['name']}",fill='black')
 sheet.paste(tile,((idx%5)*470,(idx//5)*480))
sheet.save(out/'flux2_contact_sheet.jpg',quality=90)
print('FLUX_DONE',sum(r['status']=='ok' for r in results),'/',len(results),flush=True)
