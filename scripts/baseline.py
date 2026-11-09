import os,time,json,traceback,torch
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import transformers.utils
transformers.utils.FLAX_WEIGHTS_NAME='flax_model.msgpack'
from diffusers import StableDiffusionPipeline,DPMSolverMultistepScheduler
OUT=Path('/warehouse/illustrations/2026-11-09_image-benchmark')
OUT.mkdir(parents=True,exist_ok=True)
torch.backends.cuda.matmul.allow_tf32=True
jobs=[
(1,'red_apple','a single red apple with precisely one attached green leaf on a plain white tabletop, plain white background, soft shadow, clean studio still life',512,512),
(2,'teapot_pears','a blue ceramic teapot on a dark wooden table. Exactly two yellow pears, one to the left of the teapot is lying horizontally, one to the right stands vertically. Still-life composition, precise arrangement',640,512),
(3,'lightbulb_greenhouse','an enormous transparent incandescent lightbulb upright on a wooden plinth, containing a miniature greenhouse with ferns and a tiny wooden park bench inside the glass bulb, whimsical isometric cutaway illustration',512,640),
(4,'wet_bicycle','a single vintage bicycle parked on rainy cobblestones at night, exactly one front wheel partly submerged in a puddle, bicycle and illuminated streetlamp reflected accurately in the puddle, cinematic lighting',640,512),
(5,'spiral_tree_train','a colossal ancient tree trunk with a spiral railroad making exactly three loops around the trunk, a miniature five-car train climbing its tracks, first carriage emerging from behind the far side of the trunk, detailed fantasy scene',640,512),
(6,'clockwork_whale','a flying mechanical whale high in the sky, half its body covered with transparent glass shell revealing actual brass gears and interlocking axles, left pectoral fin raised and right pectoral fin lowered, elaborate steampunk illustration',640,512),
(7,'mirror_chess','a chessboard directly in front of a tall flat mirror, exactly three pieces on the board: one white king, one black queen, one white rook, mirror reflects the correct piece positions and silhouettes, perspective accurate',640,512),
(8,'four_level_city','detailed cross-sectional elevation of an underground city with exactly four horizontal levels. top floor is a green farm. second floor is a busy market. third floor is residential apartments. bottom fourth floor is a glowing power station. ONE vertical elevator shaft connects all four floors, architectural diagram',640,768),
(9,'explorer_four_views','four-panel character model sheet of the SAME woman explorer: short silver hair, orange jacket, a small scar on her LEFT cheek, backpack. Panel one front view, panel two side view, panel three back view, panel four running action pose. consistent outfit and anatomy across panels, character turnaround',768,512),
(10,'time_hourglass','giant transparent hourglass floating above a stormy ocean, inside upper bulb a morning harbor town with houses and a lighthouse; inside lower bulb the EXACT SAME town seen at night with buildings in identical positions; glowing grains of sand flowing through center; realistic refraction of sea and sky in glass, epic fantasy artwork',640,768)
]
base='masterpiece, high quality, richly detailed illustration, beautiful composition, '
negative='bad quality, blurry, lowres, deformed, broken, artifacts, watermark, signature, text, logo, cropped, distorted perspective, extra objects'
pipe=StableDiffusionPipeline.from_pretrained('/workspace/models/counterfeit-v25',torch_dtype=torch.float16,local_files_only=True,safety_checker=None,requires_safety_checker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True,algorithm_type='dpmsolver++')
pipe=pipe.to('cuda')
pipe.enable_vae_slicing()
results=[]
for lv,name,descr,w,h in jobs:
  t=time.time();seed=20261109+lv*173;status='ok';error=None
  try:
    torch.cuda.reset_peak_memory_stats()
    im=pipe(prompt=base+descr,negative_prompt=negative,width=w,height=h,num_inference_steps=23,guidance_scale=7.0,generator=torch.Generator('cuda').manual_seed(seed)).images[0]
    im.save(OUT/f'lv{lv:02d}_baseline.png')
    vram=round(torch.cuda.max_memory_reserved()/1024**3,2)
    print('SAVED',lv,name,round(time.time()-t,1),'sec vram',vram,flush=True)
  except Exception as e:
    status='failed';error=str(e);vram=None
    print('ERROR',lv,name,repr(e),flush=True)
    try:torch.cuda.empty_cache()
    except:pass
  results.append({'level':lv,'name':name,'prompt':base+descr,'seed':seed,'width':w,'height':h,'steps':23,'cfg':7.0,'seconds':round(time.time()-t,2),'peak_reserved_GiB':vram,'status':status,'error':error,'filename':f'lv{lv:02d}_baseline.png'})
  (OUT/'baseline.json').write_text(json.dumps({'model':'gsdf/Counterfeit-V2.5','gpu':'RTX3060Ti','items':results},ensure_ascii=False,indent=2))
if all(r['status']=='ok' for r in results):
    tiles=[]
    for r in results:
      im=Image.open(OUT/r['filename']).convert('RGB')
      im.thumbnail((448,448))
      tile=Image.new('RGB',(470,480),'white')
      tile.paste(im,((470-im.width)//2,(448-im.height)//2))
      d=ImageDraw.Draw(tile);d.text((14,455),f"Lv{r['level']}: {r['name']}",fill='black')
      tiles.append(tile)
    sheet=Image.new('RGB',(470*5,480*2),'white')
    for i,im in enumerate(tiles):sheet.paste(im,((i%5)*470,(i//5)*480))
    sheet.save(OUT/'baseline_contact_sheet.jpg',quality=90)
print('BASELINE_DONE',sum(x['status']=='ok' for x in results),'/10',flush=True)
