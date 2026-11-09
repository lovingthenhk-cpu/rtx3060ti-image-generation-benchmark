import json,time,torch
from pathlib import Path
import transformers.utils
transformers.utils.FLAX_WEIGHTS_NAME='flax_model.msgpack'
from PIL import Image,ImageDraw
from diffusers import StableDiffusionXLPipeline,DPMSolverMultistepScheduler
OUT=Path('/warehouse/illustrations/2026-11-09_image-benchmark')
print('ANIMAGINE_START',flush=True)
pipe=StableDiffusionXLPipeline.from_pretrained('/workspace/models/animagine-xl-3.1',torch_dtype=torch.float16,local_files_only=True,add_watermarker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True)
pipe=pipe.to('cuda');pipe.enable_vae_slicing();pipe.set_progress_bar_config(disable=True)
jobs=[
(7,'chessboard in front of an old mirror, exactly one white king, one black queen, and one white rook on a chessboard, all three pieces accurately reflected in mirror, perspective, masterful fantasy illustration'),
(9,'four-panel reference sheet of the same female explorer in orange jacket, silver short hair, backpack, LEFT cheek scar; FRONT VIEW, LEFT SIDE VIEW, REAR VIEW, RUNNING POSE, same clothing all four panels, full bodies, anime art'),
(10,'fantasy transparent hourglass floating on ocean storm, upper bulb contains sunny morning harbor village with lighthouse and roofs, lower bulb contains the identical harbor village at night with matching building positions, gold sand flowing at center, ornate glass, anime fantasy art')
]
rows=json.loads((OUT/'animagine.json').read_text())['items'][:1]
for lv,prompt in jobs[1:]:
 t=time.monotonic()
 try:
  torch.cuda.reset_peak_memory_stats()
  im=pipe(prompt=prompt,negative_prompt='blurry, watermark, text, logo, extra objects, deformed geometry, duplicate character, missing limbs',width=640,height=384,num_inference_steps=25,guidance_scale=7,generator=torch.Generator('cuda').manual_seed(20261109+lv*11)).images[0]
  path=OUT/f'lv{lv:02d}_animagine.png';im.save(path)
  rec={'level':lv,'status':'ok','filename':path.name,'prompt':prompt,'seconds':round(time.monotonic()-t,2),'peak_reserved_GiB':round(torch.cuda.max_memory_reserved()/1024**3,2),'seed':20261109+lv*11,'steps':25,'cfg':7,'width':640,'height':384}
 except Exception as e:
  rec={'level':lv,'status':'error','error':str(e),'seconds':round(time.monotonic()-t,2)}
 rows.append(rec);(OUT/'animagine.json').write_text(json.dumps({'model':'Animagine XL 3.1','items':rows},ensure_ascii=False,indent=2))
 print('ANIMAGINE',lv,rec['status'],rec['seconds'],rec.get('error',''),flush=True)
print('ANIMAGINE_DONE',len([x for x in rows if x['status']=='ok']),flush=True)
