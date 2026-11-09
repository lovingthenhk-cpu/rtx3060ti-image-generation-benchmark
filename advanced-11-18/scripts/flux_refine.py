import time,json,urllib.request,urllib.parse,shutil,os
from pathlib import Path
from PIL import Image
D=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
P=Path('/workspace/ComfyUI/input');P.mkdir(exist_ok=True,parents=True)
port=int(Path('/workspace/flux2-port.txt').read_text().strip());base='http://127.0.0.1:'+str(port)
cases=[
(14,'Symmetrical top down photograph of a highly detailed twelve-arm bronze and crystal chandelier. EXACTLY 12 arms at equal 30 degree intervals. Eleven lamps glowing, exactly one dark unlit lamp in the 2 oclock position. Keep identical positions and count.',640,640,.32),
(16,'Five floating rocky islands, each connected to exactly two neighbors by five wooden bridges in one pentagonal loop. No diagonal bridges. Maintain original five-island layout and connections. Gorgeous fantasy game environment, lush trees, detailed rocks, bright daylight.',640,512,.30)
]
def get(path):
 with urllib.request.urlopen(base+path,timeout=40) as f:return json.load(f)
def post(nodes):
 rq=urllib.request.Request(base+'/prompt',json.dumps({'prompt':nodes,'client_id':'advanced-refine'}).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(rq,timeout=40) as f:return json.load(f)
res=[]
for lv,prompt,w,h,denoise in cases:
 f=f'lv{lv:02d}_constructed.png';shutil.copy2(D/f,P/f)
 nodes={
 '1':{'class_type':'UNETLoader','inputs':{'unet_name':'flux-2-klein-4b-fp8.safetensors','weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_4b_fp4_flux2.safetensors','type':'flux2','device':'default'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':'flux2-vae.safetensors'}},
 '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},
 '5':{'class_type':'ConditioningZeroOut','inputs':{'conditioning':['4',0]}},
 '6':{'class_type':'CFGGuider','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'cfg':1.0}},
 '7':{'class_type':'RandomNoise','inputs':{'noise_seed':202611100+lv}},
 '8':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},
 '9':{'class_type':'Flux2Scheduler','inputs':{'steps':8,'width':w,'height':h}},
 '11':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['7',0],'guider':['6',0],'sampler':['8',0],'sigmas':['17',0],'latent_image':['16',0]}},
 '12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['3',0]}},
 '13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':'benchmark_refined'}},
 '14':{'class_type':'LoadImage','inputs':{'image':f}},
 '15':{'class_type':'ImageScale','inputs':{'image':['14',0],'upscale_method':'lanczos','width':w,'height':h,'crop':'disabled'}},
 '16':{'class_type':'VAEEncode','inputs':{'pixels':['15',0],'vae':['3',0]}},
 '17':{'class_type':'SplitSigmasDenoise','inputs':{'sigmas':['9',0],'denoise':denoise}}
 }
 st=time.monotonic();row={'level':lv,'status':'unknown','prompt':prompt,'denoise':denoise,'steps':8,'width':w,'height':h,'seed':202611100+lv,'source':f,'filename':f'lv{lv:02d}_flux_refined.png'}
 try:
  pid=post(nodes)['prompt_id']
  for _ in range(100):
   time.sleep(3);hist=get('/history/'+pid)
   if pid not in hist:continue
   if hist[pid].get('status',{}).get('status_str')=='error':raise RuntimeError(str(hist[pid].get('status')))
   imgs=hist[pid].get('outputs',{}).get('13',{}).get('images',[])
   if imgs:
    with urllib.request.urlopen(base+'/view?filename='+urllib.parse.quote(imgs[0]['filename'])+'&type=output',timeout=50) as f:(D/row['filename']).write_bytes(f.read())
    row['status']='ok';break
  if row['status']!='ok':raise RuntimeError('timeout')
 except Exception as e:row['status']='error';row['error']=str(e)[:500]
 row['seconds']=round(time.monotonic()-st,2)
 res.append(row);(D/'flux_refined.json').write_text(json.dumps({'items':res},indent=2))
 print('REFINE',lv,row['status'],row['seconds'],row.get('error',''),flush=True)
