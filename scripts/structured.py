import time,json,math,traceback
from pathlib import Path
import numpy as np,torch
import transformers.utils
transformers.utils.FLAX_WEIGHTS_NAME='flax_model.msgpack'
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
from diffusers import StableDiffusionPipeline,StableDiffusionImg2ImgPipeline,DPMSolverMultistepScheduler
OUT=Path('/warehouse/illustrations/2026-11-09_image-benchmark')
OUT.mkdir(exist_ok=True,parents=True)
torch.backends.cuda.matmul.allow_tf32=True
pipe=StableDiffusionPipeline.from_pretrained('/workspace/models/counterfeit-v25',torch_dtype=torch.float16,local_files_only=True,safety_checker=None,requires_safety_checker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True,algorithm_type='dpmsolver++')
pipe.to('cuda');pipe.enable_vae_slicing()
negative='blurry, extra objects, text, logo, watermark, clutter, broken geometry, multiple copies'
records=[]
def gen(key,prompt,w,h,seed,steps=24):
 t=time.monotonic()
 x=pipe(prompt='masterpiece, high quality illustration, '+prompt,negative_prompt=negative,width=w,height=h,num_inference_steps=steps,guidance_scale=7.0,generator=torch.Generator('cuda').manual_seed(seed)).images[0]
 path=OUT/(key+'.png');x.save(path)
 records.append({'key':key,'prompt':prompt,'width':w,'height':h,'seed':seed,'steps':steps,'seconds':round(time.monotonic()-t,2)})
 (OUT/'structured.json').write_text(json.dumps(records,indent=2))
 print('ASSET',key,round(time.monotonic()-t,2),flush=True)
 return x
def cutout(im):
 im=im.convert('RGB')
 a=np.array(im,dtype=np.uint8);l=np.min(a,axis=2).astype(np.float32)
 alpha=np.clip((244-l)/55.,0,1)
 # neutral white bg segmentation: works best when white prompt obeyed
 yy,xx=np.where(alpha>0.35)
 if not len(xx):return im.convert('RGBA')
 box=(max(0,int(xx.min())-10),max(0,int(yy.min())-10),min(im.width,int(xx.max())+11),min(im.height,int(yy.max())+11))
 im=im.crop(box);alpha=(alpha*255).astype('uint8')
 mask=Image.fromarray(alpha,'L').crop(box).filter(ImageFilter.GaussianBlur(1))
 im=im.convert('RGBA');im.putalpha(mask);return im
def put_layer(canvas,im,rect,shadow=True):
 cut=cutout(im);cut.thumbnail((rect[2],rect[3]),Image.Resampling.LANCZOS)
 x=rect[0]+(rect[2]-cut.width)//2;y=rect[1]+(rect[3]-cut.height)//2
 if shadow:
  sh=Image.new('RGBA',cut.size,(0,0,0,0));black=Image.new('RGBA',cut.size,(30,24,18,70))
  sh.paste(black,(0,0),cut.getchannel('A'));sh=sh.filter(ImageFilter.GaussianBlur(8))
  canvas.alpha_composite(sh,(x+5,y+9))
 canvas.alpha_composite(cut,(x,y))
 return {'x':x,'y':y,'size':cut.size}
# Level 2: exact object placement, independently generated 4 assets
bg=gen('asset02_background','empty bare dark wooden table, no objects, pale gray wall, warm sidelight, tabletop occupies lower two-thirds of composition',640,512,8011)
tp=gen('asset02_teapot','ONE cobalt blue ceramic Japanese teapot with spout and handle, object fully visible, CENTERED ISOLATED on PURE WHITE background',384,384,8012)
pl=gen('asset02_pear_left','ONE ripe yellow pear LYING horizontally sideways on a pure white background, isolated food product',384,384,8013)
pr=gen('asset02_pear_right','ONE ripe yellow pear STANDING UPRIGHT vertically on a pure white background, isolated fruit',384,384,8014)
canvas=bg.convert('RGBA')
puts=[put_layer(canvas,pl,(23,260,180,180)),put_layer(canvas,tp,(212,190,220,255)),put_layer(canvas,pr,(460,250,155,192))]
canvas.convert('RGB').save(OUT/'lv02_composite.png')
print('COMPOSITE 02',puts,flush=True)
# Level 8: independent floor bands, ensure precise order and one continuous elevator shaft
bands=[
 ('farm','cross section interior of underground hydroponic vegetable farm floor, rows of green crops, growers, architectural cutaway, left side panorama'),
 ('market','cross section interior of underground marketplace, food stalls, merchants, colorful goods, architectural cutaway'),
 ('homes','cross section interior of underground residential apartments, windows and rooms and furniture, architectural cutaway'),
 ('power','cross section interior of underground electrical power plant, glowing transformers and turbines, architectural cutaway')
]
layers=[]
for i,(key,prompt) in enumerate(bands):
 im=gen(f'asset08_{key}',prompt,640,256,8200+i);layers.append(im)
city=Image.new('RGB',(640,896),(31,33,41))
for i,(name,_) in enumerate(bands):
 layer=layers[i].resize((640,224),Image.Resampling.LANCZOS)
 city.paste(layer,(0,i*224))
d=ImageDraw.Draw(city)
for j in range(1,4):d.rectangle((0,j*224-4,640,j*224+4),fill=(82,77,70))
d.rectangle((560,0,622,895),fill=(36,39,45),outline=(180,166,120),width=5)
d.rectangle((570,0,614,895),outline=(143,173,188),width=3)
for y in [112,336,560,784]:
 d.rectangle((563,y-18,617,y+18),fill=(91,111,122),outline=(241,224,149),width=3)
d.text((12,14),'01 FARM',fill=(255,255,255))
d.text((12,238),'02 MARKET',fill=(255,255,255))
d.text((12,462),'03 HOMES',fill=(255,255,255))
d.text((12,686),'04 POWER',fill=(255,255,255))
city.save(OUT/'lv08_composite.png');print('COMPOSITE 08',flush=True)
# Level 9: independent viewpoints with shared immutable identity tokens
views=[
 ('front','front-facing full body character portrait, standing neutral front view'),
 ('side','full body profile viewed from LEFT side, side-facing character portrait'),
 ('back','full body portrait from BEHIND, back view showing backpack straps'),
 ('running','full body running motion pose towards the right, dynamic action')
]
sheet=Image.new('RGB',(1536,544),(240,239,233))
for i,(key,pose) in enumerate(views):
 prompt='the same adult woman adventurer, short silver bob haircut, bright orange jacket, brown travel backpack, dark blue trousers, brown boots, small scar on her left cheek, '+pose+', one person only, clean light studio background'
 im=gen(f'asset09_{key}',prompt,384,512,9300+i)
 sheet.paste(im,(i*384,0))
 ImageDraw.Draw(sheet).text((i*384+12,518),key.upper(),fill=(35,35,35))
sheet.save(OUT/'lv09_composite.png');print('COMPOSITE 09',flush=True)
# Level 10: the two harbors share identical source pixels; edited lighting retains architecture exactly
day=gen('asset10_day_harbor','wide cinematic panorama of a small coastal harbor town with one lighthouse on the left, clustered stone houses, docks and boats, clear morning sunlight, eye level, picturesque storybook detailed architecture',576,288,10101)
night=ImageEnhance.Brightness(day).enhance(.25)
night=ImageEnhance.Color(night).enhance(.6)
arr=np.asarray(night.convert('RGB'),dtype=np.uint8).copy()
arr[:,:,2]=np.clip(arr[:,:,2].astype(float)*1.55+18,0,255).astype('uint8')
night=Image.fromarray(arr,'RGB')
b=Image.open(OUT/'lv10_baseline.png').convert('RGB').resize((640,768))
ov=b.copy().convert('RGBA')
# glass compartments: upper triangle inward, lower triangle outward; mask clips daytime/nighttime
mask_top=Image.new('L',(640,768));mask_bot=Image.new('L',(640,768))
mt=ImageDraw.Draw(mask_top);mb=ImageDraw.Draw(mask_bot)
mt.polygon([(156,98),(487,98),(321,362)],fill=228)
mb.polygon([(321,410),(156,670),(487,670)],fill=228)
top=Image.new('RGBA',(640,768));bottom=Image.new('RGBA',(640,768))
top.paste(day.resize((640,384)),(0,38));bottom.paste(night.resize((640,384)),(0,381))
ov.paste(top,(0,0),mask_top);ov.paste(bottom,(0,0),mask_bot)
d=ImageDraw.Draw(ov)
d.line([(156,98),(487,98),(321,362),(321,410),(156,670),(487,670),(321,410)],fill=(190,225,249,230),width=8)
d.ellipse((308,365,333,415),fill=(250,213,120,230))
ov.convert('RGB').save(OUT/'lv10_composite.png')
print('COMPOSITE 10',flush=True)
# high-res per-composition enhancement via 1.5x image-to-image denoise=0.20
try:
 imgpipe=StableDiffusionImg2ImgPipeline(**pipe.components)
 imgpipe.set_progress_bar_config(disable=True)
 for lv,prompt in [(2,'a blue teapot between two yellow pears on wooden table, left pear lying horizontal, right pear standing upright, integrated still life illustration'),
                   (8,'cutaway of a four-level underground city: farm, market, residential, power, single connecting elevator')]:
  src=Image.open(OUT/f'lv{lv:02d}_composite.png').convert('RGB')
  w=round(src.width*1.25/8)*8;h=round(src.height*1.25/8)*8
  if w*h>900000:continue
  src=src.resize((w,h),Image.Resampling.LANCZOS)
  t=time.monotonic()
  result=imgpipe(prompt=prompt,negative_prompt=negative,image=src,strength=.20,num_inference_steps=25,guidance_scale=6.0,generator=torch.Generator('cuda').manual_seed(11000+lv)).images[0]
  result.save(OUT/f'lv{lv:02d}_refined.png')
  print('REFINED',lv,'size',w,h,'secs',round(time.monotonic()-t,2),flush=True)
except Exception as ex:
 print('REFINE_FAIL',repr(ex),flush=True)
 (OUT/'refine_error.txt').write_text(traceback.format_exc())
print('STRUCTURED_DONE',len(records),'assets',flush=True)
