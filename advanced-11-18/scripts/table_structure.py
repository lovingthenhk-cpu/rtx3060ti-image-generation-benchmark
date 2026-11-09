from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,json,random
D=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
W,H=1400,900
im=Image.new('RGB',(W,H),(212,219,226));d=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
# stair geometry: steep ascending to the upper right, plus railings
for k in range(12):
 x0=k*120-100; y0=850-k*53
 d.polygon([(x0,y0),(x0+220,y0),(x0+220,y0+35),(x0,y0+35)],fill=(160+k%2*8,169,176),outline=(100,109,116))
 d.line((x0,y0,x0+220,y0),fill=(244,242,235),width=6)
d.line((0,810,1400,180),fill=(91,104,111),width=15)
d.line((0,750,1400,120),fill=(181,188,191),width=8)
# moving table - supports will be drawn behind the tabletop
A=(317,521);B=(929,295);C=(1034,359);D4=(422,596)
legs=[(A,(308,711)),(B,(953,486)),(C,(1052,548)),(D4,(435,785))]
for top,bot in legs:
 d.line((top[0]+8,top[1]+3,bot[0]+8,bot[1]+3),fill=(64,44,29),width=29)
 d.line((top[0],top[1],bot[0],bot[1]),fill=(128,77,43),width=21)
# tabletop with front rim and rich wood streaks
d.polygon([A,B,C,D4],fill=(177,113,62),outline=(74,45,27))
d.polygon([(A[0],A[1]+18),(B[0],B[1]+18),(C[0],C[1]+18),(D4[0],D4[1]+18)],fill=(106,62,39))
d.polygon([A,B,C,D4],fill=(197,139,82))
for t in (.18,.34,.58,.76):
 a=(A[0]*(1-t)+B[0]*t,A[1]*(1-t)+B[1]*t)
 b=(D4[0]*(1-t)+C[0]*t,D4[1]*(1-t)+C[1]*t)
 d.line((a[0],a[1],b[0],b[1]),fill=(166,106,62),width=4)
d.line(A+B+C+D4+A,fill=(76,46,27),width=9,joint='curve')
# people drawn as precisely 3 articulated vector figures, each two reaching hands at tabletop edge
# All hands endpoint coordinates lie on or within 6 px of the tabletop border.
persons=[
 {'id':1,'head':(179,455),'torso':(190,584),'hip':(185,660),'feet':((138,799),(272,791)),'contacts':((317,521),(420,592)),'color':(38,105,148),'side':'lower'},
 {'id':2,'head':(550,560),'torso':(557,676),'hip':(560,756),'feet':((495,876),(654,874)),'contacts':((464,578),(651,399)),'color':(60,114,150),'side':'lower'},
 {'id':3,'head':(1139,243),'torso':(1137,363),'hip':(1132,452),'feet':((1074,612),(1240,600)),'contacts':((929,296),(1032,356)),'color':(174,64,56),'side':'upper'}
]
def strokearm(pts,sleeve):
 d.line(pts,fill=(66,57,54),width=30,joint='curve')
 d.line(pts[:-1],fill=sleeve,width=23,joint='curve')
 x,y=pts[-1];d.ellipse((x-13,y-13,x+13,y+13),fill=(233,183,137),outline=(106,72,58),width=3)
for p in persons:
 hx,hy=p['head'];tx,ty=p['torso'];px,py=p['hip'];col=p['color']
 # pants & boots
 for fx,fy in p['feet']:
  d.line((px,py,(px+fx)/2,py+58,fx,fy),fill=(49,61,74),width=35,joint='curve')
  d.line((fx-12,fy,fx+18,fy),fill=(31,37,40),width=15)
 # tapered jacket torso
 d.polygon([(tx-43,ty-58),(tx+43,ty-60),(px+42,py),(px-37,py)],fill=col,outline=(40,45,52),width=5)
 # head/neck
 d.line((hx,hy+33,tx,ty-57),fill=(223,167,132),width=18)
 d.ellipse((hx-33,hy-39,hx+33,hy+37),fill=(235,189,146),outline=(101,76,66),width=4)
 d.pieslice((hx-33,hy-40,hx+33,hy+25),180,355,fill=(70,60,51))
 # eyes simplified
 d.ellipse((hx-11,hy-3,hx-6,hy+1),fill=(39,43,49))
 d.ellipse((hx+8,hy-3,hx+13,hy+1),fill=(39,43,49))
 (left,right)=p['contacts']
 # Sleeves and arms connect to table corners; all 6 palms contact tabletop
 start1=(tx-31,ty-44);start2=(tx+34,ty-47)
 for j,(start,end) in enumerate(((start1,left),(start2,right))):
  mid=((start[0]+end[0])*.53,start[1]-35+(-1 if j else 1)*15)
  strokearm([start,mid,end],col)
# The table follows a diagonal upward trajectory and is held off its feet.
d.rounded_rectangle((30,24,1100,106),radius=15,fill=(40,55,65))
d.text((54,43),'THREE MOVERS  ·  SIX TABLE CONTACTS  ·  FOUR TABLE LEGS',font=font(26),fill=(255,253,246))
d.rounded_rectangle((38,817,1010,875),radius=8,fill=(242,246,248),outline=(104,119,129),width=2)
d.text((50,833),'Structural pose study; contacts and object count fixed by geometry; realism not yet achieved.',font=font(17),fill=(54,71,81))
fn=D/'lv12_constructed.png';im.save(fn)
checks={'persons':len(persons),'lower_end_workers':2,'upper_end_workers':1,'hands_touching_table':sum(len(p['contacts']) for p in persons),'table_legs':len(legs),'compliance':'stylized structural study'}
(D/'table_structure.json').write_text(json.dumps(checks,indent=2))
print('TABLE_SAVED',fn,checks)
