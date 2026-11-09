from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
import numpy as np, math, random, json, time
OUT=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(s):return ImageFont.truetype(fontpath,s)
results={}
def save(lv,im,checks):
 fn=f'lv{lv:02d}_constructed.png';im.convert('RGB').save(OUT/fn)
 results[lv]={'file':fn,'checks':checks}
 (OUT/'physical.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
 print('PHYSICAL',lv,fn,checks,flush=True)
# 15: Actual vector Snell-law refraction through three spheres for straight camera rays.
W,H=1300,850
yy,xx=np.mgrid[:H,:W].astype(np.float32)
x=xx.copy();y=yy.copy()
def wall(X,Y):
 phase=np.mod(np.floor((X+13)/42),2)
 col=np.empty((H,W,3),dtype=np.float32)
 col[:,:,0]=np.where(phase==0,193,45)
 col[:,:,1]=np.where(phase==0,55,95)
 col[:,:,2]=np.where(phase==0,61,169)
 # brighter upper wall than bottom wall; dark panel separators
 val=0.72+0.18*(1-Y/H)
 for i in range(3):col[:,:,i]=col[:,:,i]*val
 return col
canvas=wall(x,y)
# foreground/table begins at y=645 with beige tabletop and soft caustics
table=yy>650
for i,v in enumerate((202,194,184)):
 canvas[:,:,i]=np.where(table,v-(yy-650)*.055,canvas[:,:,i])
# procedural shadow and focused light pool on tabletop for each sphere
spheres=[(285.,490.,158.,-0.1),(705.,520.,128.,0.0),(1036.,548.,101.,0.1)]
for cx,cy,R,cz in spheres:
 ox=(xx-cx)/R;oy=(yy-672)/(R*.21)
 shadow=np.exp(-2.2*(ox**2+oy**2))
 flare=np.exp(-((xx-cx-38)**2/(R*.4)**2+(yy-663)**2/(R*.1)**2))
 for i in range(3):
  canvas[:,:,i]=np.where(table,canvas[:,:,i]*(1-.24*shadow)+np.array((30,22,9))[i]*flare,canvas[:,:,i])
# compute refracted intersection of each pixel ray through analytic glass sphere, n=1.5, back stripe wall.
for cx,cy,R,cz in spheres:
 dx=xx-cx;dy=yy-cy;rho2=dx**2+dy**2
 mask=rho2<R**2
 # camera rays along z+, intersection P at front, refraction to glass n1/n2
 sq=np.sqrt(np.maximum(R**2-rho2,0))
 nx=dx/R;ny=dy/R;nz=-sq/R
 cosi=-nz;eta=1/1.5
 K=np.maximum(0.,1-eta**2*(1-cosi**2))
 kroot=np.sqrt(K)
 tx=(eta*cosi-kroot)*nx;ty=(eta*cosi-kroot)*ny;tz=eta+(eta*cosi-kroot)*nz
 # second sphere hit; geometric distance inside
 t=2*(sq*tz-dx*tx-dy*ty)/(tx**2+ty**2+tz**2)
 P2x=dx+t*tx;P2y=dy+t*ty;P2z=-sq+t*tz+cz
 nx2=P2x/R;ny2=P2y/R;nz2=(P2z-cz)/R
 cos2=tx*nx2+ty*ny2+tz*nz2
 eta2=1.5;K2=np.maximum(0.,1-eta2**2*(1-cos2**2))
 factor=eta2*cos2-np.sqrt(K2)
 outx=eta2*tx-factor*nx2;outy=eta2*ty-factor*ny2;outz=eta2*tz-factor*nz2
 safe=np.where(np.abs(outz)>0.02,outz,0.02)
 backx=cx+P2x+outx/safe*(2.8-P2z)
 backy=cy+P2y+outy/safe*(2.8-P2z)
 refr=wall(backx,backy)
 edge=np.sqrt(np.clip(rho2,0,R**2))/R
 # glass edge dark Fresnel, central slight haze and specular
 dark=.76+.18*(1-edge**5)
 for i in range(3):
  canvas[:,:,i]=np.where(mask,refr[:,:,i]*dark+np.array([22,24,32])[i]*(1-dark),canvas[:,:,i])
 glint=np.exp(-((dx+R*.36)/(R*.16))**2-((dy+R*.48)/(R*.21))**2)
 ring=np.exp(-((edge-.98)/.035)**2)
 for i in range(3):
  canvas[:,:,i]=np.where(mask,canvas[:,:,i]+glint*130+ring*56,canvas[:,:,i])
im=Image.fromarray(np.uint8(np.clip(canvas,0,255)),'RGB');d=ImageDraw.Draw(im)
d.line((0,648,W,648),fill=(116,111,113),width=5)
d.rounded_rectangle((19,18,915,85),radius=12,fill=(23,29,38))
d.text((40,37),'THREE GLASS SPHERES   •   TWO SNELL REFRACTIONS PER RAY',font=font(22),fill=(246,242,238))
save(15,im,{'spheres':3,'refraction':'analytic Snell n_air=1,n_glass=1.5 on orthographic rays','shadows':'stylized, not calibrated physical caustics','stripe_frequency_pixels':42})
# 17: co-axial exploded pocket watch. 8 primary named stages, 2 hands on one stage.
W,H=1550,960;im=Image.new('RGB',(W,H),(241,242,239));d=ImageDraw.Draw(im)
for x in range(0,W,70):d.line((x,0,x,H),fill=(228,230,227),width=1)
for y in range(0,H,70):d.line((0,y,W,y),fill=(228,230,227),width=1)
d.text((35,24),'COAXIAL EXPLODED VIEW   /   ANTIQUE POCKET WATCH',font=font(31),fill=(36,48,54))
# center line: all part centers on same inclined assembly axis, axis visual
center=[(140+149*i,195+77*i) for i in range(9)]
d.line((52,150,1450,875),fill=(173,175,179),width=3)
def disc(cx,cy,r,top=(196,170,119),thickness=12):
 # horizontally stretched watch disk ellipse with bevel
 d.ellipse((cx-r,cy-r*.48+thickness,cx+r,cy+r*.48+thickness),fill=(120,91,53),outline=(61,54,47),width=4)
 d.ellipse((cx-r,cy-r*.48,cx+r,cy+r*.48),fill=top,outline=(77,67,48),width=5)
def ring(cx,cy,r):
 disc(cx,cy,r,top=(205,164,80),thickness=17)
 d.ellipse((cx-r+15,cy-r*.48+8,cx+r-15,cy+r*.48-8),fill=(242,242,238),outline=(102,70,35),width=6)
def gear(cx,cy,r,n=22,fill=(180,125,56)):
 pts=[]
 for k in range(n*2):
  a=math.pi*2*k/(n*2)
  rr=r if k%2==0 else r*.89
  pts.append((cx+rr*math.cos(a),cy+rr*.48*math.sin(a)))
 d.polygon(pts,fill=fill,outline=(69,58,43))
 d.ellipse((cx-r*.18,cy-r*.09,cx+r*.18,cy+r*.09),fill=(231,231,225),outline=(70,58,40),width=3)
for idx,(cx,cy) in enumerate(center):
 if idx==0:ring(cx,cy,87)
 elif idx==1: # crystal glass lens
  d.ellipse((cx-83,cy-38,cx+83,cy+38),fill=(188,222,230),outline=(78,146,165),width=5)
  d.arc((cx-62,cy-29,cx+54,cy+31),200,318,fill=(252,253,252),width=7)
 elif idx==2:
  disc(cx,cy,86,top=(240,233,208),thickness=8)
  for h in range(12):
   a=h*math.pi/6-math.pi/2
   tx=cx+71*math.cos(a);ty=cy+33*math.sin(a)
   d.text((tx-6,ty-7),str(12 if h==0 else h),font=font(10),fill=(59,51,35))
 elif idx==3: # both hands in the same coaxial stage
  d.line((cx,cy,cx-29,cy-42),fill=(49,50,57),width=11)
  d.line((cx,cy,cx+51,cy-26),fill=(60,61,64),width=6)
  d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=(237,204,121),outline=(72,62,49))
 elif idx==4:
  disc(cx,cy,85,top=(171,170,151))
  for ox,oy,r in [(-38,-15,26),(38,3,27),(0,23,19),(10,-18,20)]:gear(cx+ox,cy+oy,r)
 elif idx==5:
  disc(cx,cy,72,top=(91,110,109))
  for ox,oy,r in [(-21,-8,29),(25,12,26)]:gear(cx+ox,cy+oy,r,26)
 elif idx==6:
  disc(cx,cy,82,top=(193,149,72))
  # visible spiral mainspring inside barrel
  pts=[]
  for k in range(220):
   t=k/219*math.pi*9;r=5+k/219*60
   pts.append((cx+r*math.cos(t),cy+r*.47*math.sin(t)))
  d.line(pts,fill=(63,67,70),width=6,joint='curve')
 elif idx==7: # movement support bridge
  disc(cx,cy,80,top=(185,154,104))
  for ox,oy in [(-51,-17),(45,17),(-14,28)]:
   d.ellipse((cx+ox-8,cy+oy-8,cx+ox+8,cy+oy+8),fill=(77,75,75))
 else:
  disc(cx,cy,90,top=(203,160,78),thickness=18)
  d.ellipse((cx-65,cy-30,cx+65,cy+30),outline=(126,87,43),width=5)
 # part label on connector placed above
 names=['Bezel','Crystal','Dial','Two hands','Gear train','Pinions','Mainspring','Movement plate','Case back']
 d.text((cx-68,cy-111),f'{idx+1:02d}  {names[idx]}',font=font(16),fill=(40,55,65))
 # a guide between layer centers
 if idx<8:
  nx,ny=center[idx+1]
  d.line((cx+91,cy+44,nx-91,ny-44),fill=(101,117,129),width=2)
d.rounded_rectangle((26,840,1210,915),radius=12,fill=(230,231,225),outline=(168,173,170),width=3)
d.text((44,865),'All 9 assembly stages share one axis.  The clockwork gear train is schematic, not a verified production movement.',font=font(17),fill=(52,64,70))
collinear=all(abs((center[i][0]-center[0][0])*77-(center[i][1]-center[0][1])*149)<1e-5 for i in range(len(center)))
save(17,im,{'primary_stages':9,'center_alignment':collinear,'stage_order':['bezel','glass','dial','hands','gears','pinions','spring','movement plate','case back'],'exact_mechanical_assembly_verified':False})
# 18: Penrose-style four connected stair flights, inconsistent global rise by design.
W,H=1300,920;im=Image.new('RGB',(W,H),(222,227,229));d=ImageDraw.Draw(im)
# photo-inspired stone architecture background corridor
for x in range(0,W,130):
 d.rectangle((x,0,x+95,H),outline=(183,189,191),width=5)
for y in range(0,H,130):
 d.line((0,y,W,y),fill=(209,215,217),width=3)
d.rectangle((30,25,W-32,H-36),outline=(91,110,119),width=8)
# impossible descending global interior (a topological loop with four individually ascending segments)
corners=[(580,190),(1030,368),(790,725),(335,545)]
# draw the 4 stair ribbons as thick elevated sides, flights tilted in image plane
for i in range(4):
 x1,y1=corners[i];x2,y2=corners[(i+1)%4]
 dx=x2-x1;dy=y2-y1;L=math.hypot(dx,dy)
 px=-dy/L*56;py=dx/L*56
 poly=[(x1+px,y1+py),(x2+px,y2+py),(x2-px,y2-py),(x1-px,y1-py)]
 d.polygon(poly,fill=(161,168,174),outline=(68,85,97))
 # strong individual stair treads and risers increasing perceptual light direction
 for k in range(1,13):
  t=k/13;mx=x1+dx*t;my=y1+dy*t
  d.line((mx+px,my+py,mx-px,my-py),fill=(70,78,84),width=6)
  d.line((mx+px-4,my+py-4,mx-px-4,my-py-4),fill=(231,233,227),width=4)
 # side rail on outside
 d.line((x1+px,y1+py-12,x2+px,y2+py-12),fill=(90,104,109),width=10)
 # directional subtle arrows all clockwise "up"
 mx=x1+dx*.48;my=y1+dy*.48
 ux=dx/L;uy=dy/L
 d.line((mx-35*ux,my-35*uy,mx+35*ux,my+35*uy),fill=(229,150,55),width=6)
 d.polygon([(mx+45*ux,my+45*uy),(mx+22*ux-11*uy,my+22*uy+11*ux),(mx+22*ux+11*uy,my+22*uy-11*ux)],fill=(229,150,55))
for cx,cy in corners:
 d.polygon([(cx-67,cy-46),(cx+67,cy-46),(cx+68,cy+46),(cx-66,cy+46)],fill=(189,192,192),outline=(95,110,119))
 d.line((cx-58,cy-36,cx+58,cy-36),fill=(230,231,227),width=6)
# central black void creates architectural illusion
d.polygon([(602,324),(839,410),(714,569),(475,483)],fill=(79,91,96),outline=(48,66,72),width=7)
# upper labels
d.rounded_rectangle((41,39,1180,113),radius=12,fill=(49,65,77))
d.text((66,60),'THE IMPOSSIBLE ASCENDING LOOP  •  4 CONNECTED FLIGHTS',fill='white',font=font(26))
d.text((66,838),'All four segments individually rise in the clockwise direction. The resulting global elevation is inconsistent by design.',fill=(44,65,74),font=font(17))
save(18,im,{'four_flights':4,'connected_cycle':True,'local_uphill_directions':'clockwise all 4','global_geometry':'intentionally impossible','photorealism':'schematic, not photorealistic'})
print('PHYSICAL_DONE',len(results),flush=True)
