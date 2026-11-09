import time,json,traceback,torch
from pathlib import Path
from PIL import Image,ImageDraw
import transformers.utils
transformers.utils.FLAX_WEIGHTS_NAME='flax_model.msgpack'
from diffusers import StableDiffusionPipeline,DPMSolverMultistepScheduler
out=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
jobs=json.loads((out/'prompts.json').read_text())['items']
model='/workspace/models/counterfeit-v25'
pipe=StableDiffusionPipeline.from_pretrained(model,torch_dtype=torch.float16,local_files_only=True,safety_checker=None,requires_safety_checker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True,algorithm_type='dpmsolver++')
pipe=pipe.to('cuda');pipe.enable_vae_slicing();pipe.set_progress_bar_config(disable=True)
result=[]
for j in jobs:
 level=j['level'];start=time.monotonic();seed=20261110+137*level
 w,h=j['width'],j['height']
 try:
  torch.cuda.reset_peak_memory_stats()
  im=pipe(prompt=j['prompt'],negative_prompt='bad quality, low quality, text watermark, extra limbs, deformed hands, discontinuous shapes, artifacts',width=w,height=h,num_inference_steps=27,guidance_scale=7.0,generator=torch.Generator(device='cuda').manual_seed(seed)).images[0]
  fn=f'lv{level:02d}_counterfeit.png';im.save(out/fn)
  state='ok';peak=round(torch.cuda.max_memory_reserved()/1024**3,2);err=None
 except Exception as e:
  state='error';peak=None;err=repr(e);fn=None;torch.cuda.empty_cache()
 entry={'level':level,'status':state,'seconds':round(time.monotonic()-start,2),'peak_cuda_reserved_GiB':peak,'seed':seed,'steps':27,'cfg':7.0,'width':w,'height':h,'file':fn,'error':err}
 result.append(entry);(out/'counterfeit.json').write_text(json.dumps({'model':'Counterfeit V2.5 fp16 SD1.5','items':result},indent=2))
 print('COUNTERFEIT',level,state,entry['seconds'],peak,err or '',flush=True)
print('FINISHED',sum(x['status']=='ok' for x in result),len(result),flush=True)
