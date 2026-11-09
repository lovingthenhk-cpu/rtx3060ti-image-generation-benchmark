import json,torch,time
from pathlib import Path
from PIL import Image
import transformers.utils
transformers.utils.FLAX_WEIGHTS_NAME='flax_model.msgpack'
from diffusers import StableDiffusionImg2ImgPipeline,DPMSolverMultistepScheduler
D=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
pipe=StableDiffusionImg2ImgPipeline.from_pretrained('/workspace/models/counterfeit-v25',torch_dtype=torch.float16,local_files_only=True,safety_checker=None,requires_safety_checker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True,algorithm_type='dpmsolver++')
pipe.to('cuda');pipe.enable_vae_slicing();pipe.set_progress_bar_config(disable=True)
items=[
(12,'three adult furniture movers in work clothing lifting a large rectangular wooden dining table up the stairs, two below and one above, each both hands on furniture, four table legs, clean detailed semi-realistic painterly comic illustration',.35),
(12,'three adult furniture movers in work clothing lifting a heavy rectangular wood table together on ascending stairs, three people only, two lower and one upper, hands in contact, high quality realistic graphic novel art',.53),
(13,'precisely one polished steel marble descending a continuous sloped track from funnel into the left tip of a seesaw lever, the raised right tip of lever hitting a shiny brass bell, coherent mechanical cause-and-effect, highly detailed engineering manual with warm material textures',.33),
(14,'exactly twelve chandelier arms arranged symmetrically in radial clock positions, eleven glowing white lightbulbs and one dark unlit bulb at 2 oclock, elegant gold metallic chandelier, decorative ornate glass and bronze, detailed photographic texture',.33),
(16,'exactly five lush floating islands arranged in a pentagonal ring with precisely five wooden rope bridges making one complete loop, each island linked to two neighbors, no crossing or diagonal bridges, fantasy game environment painted aerial view',.32),
(17,'realistic exploded axonometric drawing of antique pocket watch parts, all components aligned along a single assembly axis, glass, bezel, dial, hands, clockwork gears, mainspring barrel and caseback, realistic brushed metal, engineering technical illustration',.31),
(18,'classic penrose impossible ascending staircase in four connected flights of gray stone surrounding a square void, all four rise clockwise yet the loop reconnects, Escher impossible object, architectural illustration, stone material and shadows',.32)
]
logs=[]
for level,prompt,strength in items:
 st=time.monotonic()
 src=Image.open(D/f'lv{level:02d}_constructed.png').convert('RGB')
 mw=640 if src.width>=src.height else 512
 mh=512 if src.width>=src.height else 640
 if level==14:mw=mh=640
 src=src.resize((mw,mh),Image.Resampling.LANCZOS)
 nm=f'lv{level:02d}_sdimg_{round(strength*100)}.png'
 ent={'level':level,'strength':strength,'steps':30,'prompt':prompt,'filename':nm,'width':mw,'height':mh,'seed':987110+level+int(strength*100)}
 try:
  torch.cuda.reset_peak_memory_stats()
  im=pipe(prompt=prompt,negative_prompt='blurry, clutter, extra people, extra limbs, extraneous objects, discontinuous parts, bad anatomy, watermark, text',image=src,strength=strength,num_inference_steps=30,guidance_scale=7.0,generator=torch.Generator('cuda').manual_seed(ent['seed'])).images[0]
  im.save(D/nm)
  ent['status']='ok';ent['peak_reserved_GiB']=round(torch.cuda.max_memory_reserved()/1024**3,2)
 except Exception as e:ent['status']='error';ent['error']=str(e)
 ent['seconds']=round(time.monotonic()-st,2)
 logs.append(ent);(D/'sdimg2img.json').write_text(json.dumps({'model':'Counterfeit V2.5 Img2Img','items':logs},indent=2))
 print('IMG2IMG',level,strength,ent['status'],ent['seconds'],ent.get('error',''),flush=True)
