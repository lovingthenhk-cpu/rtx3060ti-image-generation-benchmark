from pathlib import Path
import json,hashlib,re
from PIL import Image
root=Path(__file__).resolve().parents[1]
data=lambda p:json.loads((root/'data'/p).read_text())
selection=data('selections.json')['cases']
geometry=data('geometric.json')
physics=data('physical.json')
table=data('table_structure.json')
assert len(selection)==8
assert set(x['level'] for x in selection)==set(range(11,19))
for a in selection:
 p=root/'images'/a['selected']
 assert p.is_file(),p
 with Image.open(p) as im:im.verify()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
for filename in ('counterfeit.json','flux2.json'):
 a=data(filename)['items'];assert len(a)==8
 assert all(x['status']=='ok' for x in a)
for n in range(11,19):
 assert (root/'images'/f'lv{n:02d}_comparison.jpg').is_file()
g11=geometry['11']['checks'];assert g11['ribbons']==3 and g11['endpoints']==6 and g11['crossings']>0
assert table['persons']==3 and table['hands_touching_table']==6 and table['table_legs']==4 and table['lower_end_workers']==2 and table['upper_end_workers']==1
g13=geometry['13']['checks'];assert g13['funnel'] and g13['one_marble'] and g13['continuous_ramp'] and g13['bell']
g14=geometry['14']['checks'];assert g14['lamps']==12 and g14['lit_lamps']==11 and g14['angle_degrees']==30
p15=physics['15']['checks'];assert p15['spheres']==3
g16=geometry['16']['checks'];assert g16['islands']==5 and g16['bridges']==5 and g16['degrees']==[2]*5 and g16['no_crossings']
p17=physics['17']['checks'];assert p17['primary_stages']==9 and p17['center_alignment']
p18=physics['18']['checks'];assert p18['four_flights']==4 and p18['connected_cycle']
broken=[]
for name in ('README.md','REPORT.ja.md','REPORT.en.md'):
 for link in re.findall(r'\]\(([^)]+)\)',(root/name).read_text()):
  path=link.split('#')[0]
  if path and not path.startswith(('https://','http://')) and not (root/path).exists():broken.append((name,path))
assert not broken,broken
files=list((root/'images').iterdir())
for p in files:
 if p.suffix.lower() in ('.png','.jpg','.jpeg'):
  with Image.open(p) as im: im.verify()
print('PASS: selected=8; Counterfeit=8; FLUX=8; structure invariants; images=',len(files),'broken links=',len(broken))
print('NOTE: these checks do NOT validate photorealism, dynamic forces, physical caustics or visual illusion success')
