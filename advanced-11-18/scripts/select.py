from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
D=Path('/warehouse/illustrations/2026-11-10_advanced-image-benchmark')
selected={
11:('constructed','3色の経路を保持した組紐。幾何学的連続性と6端点を優先','Geometry-preserved three-strand weave, six ends'),
12:('constructed','3人・6接触・4脚を明示した搬送構図。写真らしさは未達','Three adults/six hand contacts/four legs fixed; stylized'),
13:('constructed','漏斗→坂→鉄球→シーソー→ベルの機構配置','Explicit funnel/ramp/ball/lever/bell chain'),
14:('constructed','12腕・30度・11灯点灯・1灯消灯','Exactly 12 radial arms with 11 lit and one off'),
15:('constructed','3球のガラス屈折をスネルの法則で計算。集光模様は簡略','Three glass spheres with analytic refraction; caustics simplified'),
16:('constructed','5島・5橋・次数2の閉路を保証','Five islands and five bridges, cycle degree two'),
17:('constructed','部品順序と軸一致を強制した分解模式図','Aligned exploded watch stages; assembly unverified'),
18:('flux2_variant','4辺の階段を閉路にした写真風候補。全辺の上り錯視は未検証','Photoreal four-flight closed-loop candidate; uphill illusion not proven')
}
# record critical distinctions: structure success != full prompt success.
grading={
11:('structure_pass','The three curve paths and 6 endpoints are mathematically defined; real weave/lighting remains stylized.'),
12:('structure_pass','Three human silhouettes, six contacts and four table legs; not a documentary photo or fully anatomically realistic.'),
13:('structure_partial','Visual causal linkage shown; rigid dynamics and contact timing are not simulated.'),
14:('structure_pass','Twelve radial arms equally spaced and exactly one dark lamp; material realism is illustrative.'),
15:('partial','Three refractive balls and stripes; caustics are approximate, not a physically validated illumination simulation.'),
16:('structure_pass','Five vertices, five bridges, degree two, no crossings; not fully photoreal.'),
17:('partial','Coaxial components in correct listed order, but no verified mechanical compatibility of all watch parts.'),
18:('partial','Four connected stair flights are visible; the paradoxical clockwise uphill reading is subjective/unverified.')
}
records=[]
for n,(suffix,ja,en) in selected.items():
 fn=f'lv{n:02d}_{suffix}.png';p=D/fn
 assert p.exists(),str(p)
 im=Image.open(p);im.verify()
 records.append({'level':n,'selected':fn,'status':grading[n][0],'limitations_en':grading[n][1],'notes_ja':ja,'notes_en':en,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'selections.json').write_text(json.dumps({'method':'human visual inspection + generated structural metadata, strict whole-scene compliance unverified','cases':records},ensure_ascii=False,indent=2))
for name,typ in [('selected_contact.jpg','selected'),('counterfeit_contact.jpg','counterfeit'),('flux2_contact.jpg','flux2')]:
 S=Image.new('RGB',(4*430,2*440),(249,249,249));d=ImageDraw.Draw(S)
 for idx,n in enumerate(range(11,19)):
  p=D/(selected[n][0] and f'lv{n:02d}_{selected[n][0]}.png') if typ=='selected' else D/f'lv{n:02d}_{typ}.png'
  img=Image.open(p).convert('RGB');img.thumbnail((410,398))
  x=(idx%4)*430+(430-img.width)//2;y=(idx//4)*440+(398-img.height)//2
  S.paste(img,(x,y));d.text(((idx%4)*430+13,(idx//4)*440+409),f'Lv{n} / {typ}',fill=(27,35,43))
 S.save(D/name,quality=92)
# Per case includes a direct comparison page, useful to audit real attempts visually
for n in range(11,19):
 files=[f'lv{n:02d}_counterfeit.png',f'lv{n:02d}_flux2.png',f'lv{n:02d}_constructed.png',f'lv{n:02d}_flux2_variant.png',f'lv{n:02d}_sdimg_35.png',f'lv{n:02d}_sdimg_53.png',f'lv{n:02d}_flux_refined.png']
 exists=[f for f in files if (D/f).exists()]
 sheet=Image.new('RGB',(430*min(3,len(exists)),430*((len(exists)+2)//3)),(250,250,249))
 dd=ImageDraw.Draw(sheet)
 for j,f in enumerate(exists):
  im=Image.open(D/f).convert('RGB');im.thumbnail((415,394))
  X=(j%3)*430+(430-im.width)//2;Y=(j//3)*430+(397-im.height)//2
  sheet.paste(im,(X,Y));dd.text(((j%3)*430+8,(j//3)*430+401),f.replace(f'lv{n:02d}_',''),fill=(28,35,42))
 sheet.save(D/f'lv{n:02d}_comparison.jpg',quality=88)
print('SELECTED',len(records),'cases',len(list(D.glob('*.png'))),'png files')
