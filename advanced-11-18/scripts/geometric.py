from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math, random, json, numpy as np, time
OUT=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark');OUT.mkdir(exist_ok=True,parents=True)
random.seed(201110);meta={}
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(fontpath,n)
def save(im,name,level,check):
 p=OUT/f'lv{level:02d}_{name}.png';im.save(p)
 meta[level]={'file':p.name,'checks':check,'size':im.size,'method':'deterministic geometry + procedural shading, no diffusion in this pass'}
 (OUT/'geometric.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
 print('GEOMETRIC_SAVED',level,p.name,check,flush=True)
def line(draw,points,fill,width=3):draw.line([(round(x),round(y)) for x,y in points],fill=fill,width=width,joint='curve')
def oval(d,xy,fill,outline=None,w=1):d.ellipse(xy,fill=fill,outline=outline,width=w)
# 11: EXACTLY THREE continuous color-coded paths; all crossing topology computed.
W,H=1100,720
a=np.zeros((H,W,3),dtype=np.uint8)
noise=np.random.default_rng(11).normal(0,2,(H,W,1))
for k,c in enumerate((236,227,210)):
 a[:,:,k]=np.clip(c+noise[:,:,0]+np.sin(np.arange(W)/40)[None,:]*2,0,255)
bg=Image.fromarray(a,'RGB'); im=bg.copy();d=ImageDraw.Draw(im)
# 3 single continuous ribbon strips; 6 loose endpoints; multiple over-under switches.
cols=[(180,27,46),(24,80,188),(218,162,22)]
N=1100
xs=np.linspace(80,1020,1800)
paths=[]
for i in range(3):
 phase=2*math.pi*i/3
 yy=355+127*np.sin((xs-80)/940*2*math.pi*2.7+phase)
 paths.append([(float(x),float(y)) for x,y in zip(xs,yy)])
def render_strip(pts,base,partial=False):
 if len(pts)<2:return
 shadow=tuple(max(0,v-65) for v in base)
 hi=tuple(min(255,int(v*.76+65)) for v in base)
 line(d,[(x+3,y+6) for x,y in pts],(87,71,53),46)
 line(d,pts,shadow,43)
 line(d,pts,base,36)
 line(d,[(x,y-2) for x,y in pts],hi,12)
for i in range(3):render_strip(paths[i],cols[i])
cross=[]
for i in range(3):
 for j in range(i+1,3):
  z=np.array([p[1] for p in paths[i]])-np.array([p[1] for p in paths[j]])
  ks=np.where(z[:-1]*z[1:]<0)[0]
  for k in ks:
   if 20<k<len(xs)-30:cross.append((int(k),i,j))
cross.sort()
# Cover crossings with explicit ribbon priority; record which strand passes in front.
for n,(k,i,j) in enumerate(cross):
 top=i if (n+i)%2==0 else j
 idxs=range(max(0,k-24),min(len(xs),k+25))
 render_strip([paths[top][idx] for idx in idxs],cols[top],True)
# six visible hem ends are outlined
for i,pts in enumerate(paths):
 for end in (pts[0],pts[-1]):
  x,y=end;d.line((x,y-18,x,y+18),fill=(255,242,218),width=5)
d.text((42,25),'THREE CONTINUOUS INTERWOVEN RIBBONS',font=font(25),fill=(70,54,47))
d.text((42,58),'Red  /  Blue  /  Gold    •    6 visible ends    •    crossings computed from curves',font=font(15),fill=(93,80,70))
save(im,'constructed',11,{'ribbons':3,'endpoints':6,'crossings':len(cross),'overpass_table':[(round(paths[i][k][0],1),top) for n,(k,i,j) in enumerate(cross) for top in [i if (n+i)%2==0 else j]]})
# 13: transparent mechanical chain, funnel to sloping ramp to left of seesaw, bell above right side.
W,H=1200,810;im=Image.new('RGB',(W,H),(227,232,232));d=ImageDraw.Draw(im)
for x in range(0,W,50):d.line((x,0,x,H),fill=(213,222,223),width=1)
for y in range(0,H,50):d.line((0,y,W,y),fill=(213,222,223),width=1)
d.rectangle((22,22,1178,787),outline=(68,94,105),width=7)
d.text((55,43),'MARBLE → RAMP → SEESAW → BELL',fill=(48,61,69),font=font(30))
d.text((56,88),'Connected mechanical cause-and-effect layout  •  gravity direction ↓',fill=(75,102,115),font=font(17))
# funnel at top left and exit
d.polygon([(95,150),(285,150),(219,250),(161,250)],fill=(137,149,153),outline=(41,61,72))
d.polygon([(111,158),(269,158),(211,236),(169,236)],fill=(197,208,209))
d.rectangle((176,230,205,300),fill=(126,142,150),outline=(66,82,93),width=4)
# steel ramp (ends horizontally where ball free-falls on seesaw left)
r0=(201,305);r1=(638,507)
d.line((r0[0],r0[1]+16,r1[0],r1[1]+16),fill=(58,78,85),width=24)
d.line((r0,r1),fill=(200,207,201),width=12)
for j in range(16):
 t=j/16;cx=r0[0]+(r1[0]-r0[0])*t;cy=r0[1]+(r1[1]-r0[1])*t
 d.line((cx-5,cy+10,cx+9,cy+26),fill=(93,113,115),width=3)
# support pillars under ramp
for cx in [285,460,615]:
 yy=r0[1]+(r1[1]-r0[1])*(cx-r0[0])/(r1[0]-r0[0])+13
 d.line((cx,yy,cx,705),fill=(98,114,119),width=13)
# marble, one only; falling just after ramp
ball=(661,536,704,579)
d.ellipse(ball,fill=(67,93,117),outline=(27,49,68),width=4)
d.ellipse((665,541,677,554),fill=(237,246,252))
# seesaw left down right up, central pivot
p0=(667,647);p1=(980,543);pivot=(826,598)
d.polygon([(826,610),(777,721),(872,721)],fill=(118,126,127),outline=(65,76,84))
d.line((p0,p1),fill=(74,45,33),width=26);d.line((p0,p1),fill=(195,137,72),width=18)
d.ellipse((812,584,840,612),fill=(76,76,75),outline=(209,204,175),width=3)
# bell placed at end, right tip contacts its clapper
d.line((1004,350,1004,473),fill=(80,84,84),width=15)
d.ellipse((960,460,1046,530),fill=(215,167,61),outline=(118,86,31),width=7)
d.rectangle((956,517,1051,534),fill=(166,104,31))
d.ellipse((986,528,1018,546),fill=(72,59,47))
# arrows for stages are annotations, not another marble
d.arc((618,486,734,606),15,145,fill=(224,100,48),width=6)
d.line((658,599,666,618),fill=(224,100,48),width=6)
d.arc((880,461,1010,607),198,312,fill=(224,100,48),width=6)
for num,xy,txt in [(1,(165,125),'FUNNEL'),(2,(400,330),'SLOPED TRACK'),(3,(735,680),'LEVER'),(4,(1018,401),'BELL')]:
 d.text(xy,f'{num}  {txt}',fill=(50,77,88),font=font(19))
d.text((50,757),'Static snapshot: the falling steel ball loads the left lever tip while the right tip touches the bell.',fill=(62,79,90),font=font(16))
save(im,'constructed',13,{'funnel':True,'continuous_ramp':True,'one_marble':True,'seesaw_pivot':pivot,'bell':True,'left_below_right':p0[1]>p1[1]})
# 14: 12 equally spaced luminous chandelier arms from central axis; one dark.
W=1200;H=1200;Y,X=np.mgrid[:H,:W];rad=np.sqrt((X-600)**2+(Y-600)**2)
np.random.seed(14)
a=np.zeros((H,W,3),dtype=np.uint8)
for i,c in enumerate([18,25,37]):
 a[:,:,i]=np.clip(c+24*np.maximum(0,1-rad/750)+np.random.normal(0,1.5,(H,W)),0,255)
im=Image.fromarray(a,'RGB').convert('RGBA');bloom=Image.new('RGBA',(W,H),(0,0,0,0));gl=ImageDraw.Draw(bloom)
cx=cy=600;r=423
lamps=[]
for i in range(12):
 angle=-math.pi/2+2*math.pi*i/12
 x=cx+r*math.cos(angle);y=cy+r*math.sin(angle)
 lit=(i!=2)  # 2 o'clock: unlit
 lamps.append((round(x,2),round(y,2),lit))
 if lit:
  for rr,alpha in [(110,11),(75,30),(36,60)]:
   gl.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(255,204,118,alpha))
im=Image.alpha_composite(im,bloom.filter(ImageFilter.GaussianBlur(31)))
d=ImageDraw.Draw(im)
# radial bronze spokes; equal lengths and identical assembly
for i,(x,y,lit) in enumerate(lamps):
 ang=-math.pi/2+i*math.pi/6;ux,uy=math.cos(ang),math.sin(ang)
 ax,ay=cx+90*ux,cy+90*uy
 bx,by=cx+340*ux,cy+340*uy
 d.line((ax,ay,x,y),fill=(53,35,24),width=27)
 d.line((ax-4,ay-4,x-4,y-4),fill=(186,134,75),width=13)
 for f in (0.3,0.65):
  tx=cx+(90+340*f)*ux;ty=cy+(90+340*f)*uy
  d.ellipse((tx-17,ty-17,tx+17,ty+17),fill=(204,159,89),outline=(87,63,38),width=4)
 d.ellipse((x-32,y-32,x+32,y+32),fill=(88,67,48),outline=(240,193,98),width=6)
 if lit:
  d.ellipse((x-24,y-24,x+24,y+24),fill=(255,233,175))
  d.ellipse((x-12,y-12,x+12,y+12),fill=(255,251,231))
 else:
  d.ellipse((x-24,y-24,x+24,y+24),fill=(39,43,48))
  d.ellipse((x-14,y-14,x+14,y+14),fill=(21,24,28),outline=(92,98,100),width=2)
 # dangling crystals, 12 arms
 tx=x+37*ux;ty=y+37*uy
 d.polygon([(tx,ty-18),(tx+11,ty),(tx,ty+18),(tx-11,ty)],fill=(163,194,202,165),outline=(214,231,235,220))
d.ellipse((503,503,697,697),fill=(121,83,47),outline=(227,186,105),width=13)
d.ellipse((554,554,646,646),fill=(39,36,35),outline=(192,160,104),width=10)
d.text((30,29),'12-ARM CHANDELIER  •  30° SPACING  •  ONE UNLIT',font=font(27),fill=(237,218,172))
save(im.convert('RGB'),'constructed',14,{'lamps':12,'lit_lamps':sum(k for _,_,k in lamps),'unlit_index_clockwise_from_top':2,'angle_degrees':30,'centers':lamps})
# 16: cycle graph guaranteed by adjacency list, nonintersecting pentagonal layout.
W,H=1300,980;yy,xx=np.mgrid[:H,:W]
a=np.zeros((H,W,3),dtype=np.uint8)
for i,v in enumerate((150,198,236)):
 a[:,:,i]=np.clip(v-(yy/H)*35,0,255)
im=Image.fromarray(a,'RGB').convert('RGBA');d=ImageDraw.Draw(im)
# 5 nodes in clockwise perimeter order, no edge crossings
islands=[(635,150),(1045,395),(850,760),(390,770),(180,365)]
edges=[(0,1),(1,2),(2,3),(3,4),(4,0)]
# rock undersides behind all bridges
for k,(x,y) in enumerate(islands):
 poly=[(x-104,y+8),(x-73,y+58),(x-27,y+175),(x+14,y+215),(x+73,y+87),(x+113,y+15)]
 d.polygon(poly,fill=(90,88,83,255),outline=(59,69,67,255))
 d.polygon([(x-70,y+52),(x-22,y+182),(x+14,y+215),(x+7,y+52)],fill=(122,112,98,255))
 d.ellipse((x-122,y-48,x+122,y+61),fill=(84,133,70,255),outline=(44,91,55,255),width=7)
# bridges touching island centers, drawn as rail + many parallel wooden planks
for i,j in edges:
 x1,y1=islands[i];x2,y2=islands[j]
 length=math.hypot(x2-x1,y2-y1);ux=(x2-x1)/length;uy=(y2-y1)/length
 px=-uy;py=ux
 d.line((x1,y1,x2,y2),fill=(61,52,43,255),width=39)
 d.line((x1+px*13,y1+py*13,x2+px*13,y2+py*13),fill=(196,145,81,255),width=6)
 d.line((x1-px*13,y1-py*13,x2-px*13,y2-py*13),fill=(196,145,81,255),width=6)
 for dist in range(30,int(length)-15,21):
  cx=x1+ux*dist;cy=y1+uy*dist
  d.line((cx+px*18,cy+py*18,cx-px*18,cy-py*18),fill=(173,124,76,255),width=13)
 for dist in range(48,int(length)-20,87):
  cx=x1+ux*dist;cy=y1+uy*dist
  d.line((cx+px*23,cy+py*23,cx+px*23,cy+py*23-25),fill=(90,74,58,255),width=4)
  d.line((cx-px*23,cy-py*23,cx-px*23,cy-py*23-25),fill=(90,74,58,255),width=4)
# green hubs, trees set mostly interior of the polygon away from bridge endpoints
for k,(x,y) in enumerate(islands):
 d.ellipse((x-74,y-28,x+74,y+26),fill=(109,169,83,255),outline=(66,119,66,255),width=3)
 for dx,dy in [(-35,-22),(24,-10)]:
  bx=x+dx;by=y+dy
  d.line((bx,by,bx,by-67),fill=(92,66,44,255),width=13)
  d.ellipse((bx-31,by-109,bx+31,by-42),fill=(40,106,71,255),outline=(34,85,58,255),width=4)
 d.text((x-12,y-1),str(k+1),fill=(245,245,239),stroke_fill=(32,68,38),stroke_width=3,font=font(22))
d.rounded_rectangle((31,26,750,96),radius=13,fill=(9,42,73,215))
d.text((50,45),'FIVE FLOATING ISLANDS  •  FIVE BRIDGES  •  ONE LOOP',font=font(22),fill='white')
degrees=[sum(1 for e in edges if i in e) for i in range(5)]
assert degrees==[2]*5 and len(edges)==5
save(im.convert('RGB'),'constructed',16,{'islands':5,'bridges':len(edges),'degrees':degrees,'edge_list_one_based':[[i+1,j+1] for i,j in edges],'cycle':True,'no_crossings':True})
print('ALL_PROCEDURAL_DONE',len(meta),flush=True)
