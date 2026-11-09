from pathlib import Path
from PIL import Image,ImageFilter,ImageEnhance,ImageDraw
import time,json
OUT=Path('/warehouse/illustrations/2026-11-09_image-benchmark')
rec={}
# Level 10: use FLUX hourglass, copy the exact upper harbor architecture into the lower chamber.
t=time.monotonic()
orig=Image.open(OUT/'lv10_flux2.png').convert('RGB')
target=orig.copy()
# Same pixels at changed time of day, not two independent samples.
harbor=orig.crop((121,139,395,232)).resize((276,105),Image.Resampling.LANCZOS)
harbor=ImageEnhance.Brightness(harbor).enhance(0.40)
harbor=ImageEnhance.Color(harbor).enhance(0.66)
blue=Image.new('RGB',harbor.size,(28,47,83))
harbor=Image.blend(harbor,blue,0.31)
layer=Image.new('RGB',orig.size)
layer.paste(harbor,(119,419))
mask=Image.new('L',orig.size,0)
d=ImageDraw.Draw(mask)
d.rounded_rectangle((120,422,391,521),radius=19,fill=238)
# keep the hourglass glass edges relatively intact; gradual blend
mask=mask.filter(ImageFilter.GaussianBlur(11))
target.paste(layer,(0,0),mask)
# re-introduce golden falling sand from original, so same flowing stream remains
sand=Image.new('L',orig.size,0)
d=ImageDraw.Draw(sand)
d.polygon([(242,402),(272,402),(278,522),(232,522)],fill=210)
sand=sand.filter(ImageFilter.GaussianBlur(7))
target.paste(orig,(0,0),sand)
target.save(OUT/'lv10_reference_composite.png')
rec['lv10_reference']={'status':'ok','seconds':round(time.monotonic()-t,2),'source':'lv10_flux2.png','method':'same top harbor crop, night color transform, feathered mask in lower bulb; original sand restored','limitation':'top and bottom chamber different projected scale; architectural pixel source shared but perspective and seam remain approximate'}
print('REFERENCED_HARBOR',rec['lv10_reference'],flush=True)
# Level 2: semantic segmentation vs naive white-threshold crop, CPU implementation
try:
 import rembg
 t=time.monotonic()
 session=rembg.new_session('u2netp',providers=['CPUExecutionProvider'])
 bg=Image.open(OUT/'asset02_background.png').convert('RGBA')
 items=[('pear_left',(28,265,172,172)),('teapot',(220,195,200,235)),('pear_right',(455,270,150,180))]
 for key,(x,y,w,h) in items:
  src=Image.open(OUT/f'asset02_{key}.png').convert('RGBA')
  cut=rembg.remove(src,session=session,alpha_matting=False,post_process_mask=True)
  bb=cut.getbbox()
  if bb:cut=cut.crop(bb)
  cut.thumbnail((w,h),Image.Resampling.LANCZOS)
  bg.alpha_composite(cut,(x+(w-cut.width)//2,y+(h-cut.height)//2))
 result=OUT/'lv02_rembg_composite.png';bg.convert('RGB').save(result)
 rec['lv02_rembg']={'status':'ok','seconds':round(time.monotonic()-t,2),'method':'u2netp automatic subject segmentation then spatial composition'}
 print('REMBG_SUCCESS',rec['lv02_rembg'],flush=True)
except Exception as e:
 rec['lv02_rembg']={'status':'failed','error':str(e)[:350]}
 print('REMBG_FAILED',repr(e),flush=True)
(OUT/'postprocess.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
print('POSTPROCESS_DONE',flush=True)
