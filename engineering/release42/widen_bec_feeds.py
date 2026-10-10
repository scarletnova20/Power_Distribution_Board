"""Reserve explicit copper for BEC input current and the Pi-BEC ground return.

External BEC ratings remain unknown. This is a geometry improvement, not an
assertion of the external components' ratings or fault coordination.
"""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one,Atom
import pcbnew as p
import grid_helpers as g
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_bec_feed_widths.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
raw=parse(backup.read_text())
remove_ids={'44fcce67-5d6a-41d7-9e84-c10cb35f5d0b','824f0487-a184-4718-9ff2-aa7f02951631','4d6369ab-2873-4e67-a9ff-969b432ea5ca',
            '0ff7ea9c-35c3-47ea-98bf-928c593559c8','75116bc1-9aba-4656-9a28-a5ffa6b8fc8c','3a992c45-498f-4c34-b963-8f3eca1e5f5e','9b27d1a5-c920-4ad8-aa19-12b1bb33626a'}
remove_ids.update({'06f9727e-95a6-4f62-b642-65ddd1535460','2cc51798-f8da-4c16-8ab7-5a0d3088bd44','99d28542-4c67-4968-ade0-a1ee306fb375',
 'd46304c6-8161-47f7-9bab-f323bd5f7f3d','bde3f666-a81e-4854-8d7e-7d1f1b84868d','72ebe313-a5e2-453a-8be7-af8bc73686f1',
 '8b2fafd3-4c17-422a-b91d-35200d2fe5ec','9444d71c-6e3c-4b54-b1a5-30e3ce6a669b','4db2b96b-f5f6-40ac-bfd7-46289cb1e613',
 'ab30992c-e11c-4028-924f-de9b1cdff569','d3610ded-b43e-4c8d-9ed1-cb25c8dde5e4','d559d095-13f9-41b2-945b-d3b23bec8d7b',
 'e8f7dc66-e546-4254-99ec-775b186d140a','87d1ab5f-35a5-4654-8303-61da280a8787','98db54ee-b6c6-4569-b586-fbcecc3c4c7b',
 'c29e7dad-b7bc-4b95-a770-28f2ca6abf39','6ecfef87-e52e-43e3-ab2f-f8460ccbfed2','81d90cfb-caa4-4755-b9cb-abe2d211bd56'})
remove_ids.update({'01f8b723-52b0-49ff-a42b-a6f32a5db7fd','23624b08-98ef-4820-9fa7-5c190e35acbf','913f2e6b-be66-44e6-8221-1a4d3b07635c'})
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0] in ('segment','via') and one(v,'uuid')[1] in remove_ids)]
for v in children(raw,'via'):
    if one(v,'uuid')[1]=='c8ef2ad4-73cd-4817-b794-4d3e15adcf36':one(v,'at')[1:3]=[Atom('61.2'),Atom('201.85')]
for v in children(raw,'segment'):
    if one(v,'uuid')[1]=='6168cc05-7cf8-4528-a685-245b7b1824c7':one(v,'start')[1:3]=[Atom('61.2'),Atom('202.5718')]
target.write_text(dump(raw)+'\n')
b=p.LoadBoard(str(target));fs={f.GetReference():f for f in b.GetFootprints()};g.b=b;g.fs=fs
nets={q.GetNetname():q.GetNet() for f in fs.values() for q in f.Pads() if q.GetNumber()}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def track(net,layer,width,points):
    for a,c in zip(points,points[1:]):
        t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y):
    v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
    v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);v.SetLocked(True);b.Add(v)
# The BEC1 input lies opposite the main battery-positive land. Escape left
# before changing layers; never drill an unrelated net through that top pad.
for y in (191.7,192.5,193.3):via('/Vin',66.3,y)
track('/Vin',p.B_Cu,1,[(67.5,192.5),(66.3,192.5),(66.3,191.7)])
track('/Vin',p.B_Cu,1,[(66.3,192.5),(66.3,193.3)])
track('/Vin',p.In2_Cu,1,[(66.3,197.7),(66.3,190.2),(83.7,190.2),(83.7,193.75)])
# Route outside the four J4 lands and below the mounting-hole keepout.
track('/Vin',p.B_Cu,.8,[(63,211.85),(60.2,211.85),(60.2,197.7),(66.3,197.7),(66.3,196.1)])
for y in (196.1,196.9,197.7):via('/Vin',66.3,y)
# Short BEC input bridge into the reserved regulator-input Vin copper.
track('/Vin',p.B_Cu,1,[(98,211),(96.4,209.4),(95,209.4),(95,208.6),(93.5,208.6)])
# The Pi-BEC negative input also lies opposite the top battery-positive pad.
# Its ground must reach the heavily stitched BEC1.4/J1.2 return by real copper.
track('/PGND',p.B_Cu,.8,[(71,192.5),(71,195),(78,195),(78,192.5)])
for x,y in ((61.8,207.5),(61.8,208.3),(62.4,208.3),(61.9,199.2),(62.8,199.2),(63.7,199.2)):via('/PGND',x,y)
via('/PGND',71.2686,198.0944)
# C9 is opposite a gate resistor and its bus. Screen actual opposite-face
# copper rather than assuming the resistor's orientation from its body.
_,blocked=g.masks('/PGND');c9_vias=[]
for x in (61.6,64.6,62,64.4,62.4,64):
    for y in (216.7,217.1,217.5,217.9):
        j,i=g.idx(x,y,0)[1:]
        if blocked[j-1:j+2,i-1:i+2].any():continue
        if any(math.hypot(x-a,y-c)<.79 for a,c in c9_vias):continue
        via('/PGND',x,y);c9_vias.append((x,y))
        track('/PGND',p.B_Cu,.8,[(63.2,217.375),(x,y)])
        if len(c9_vias)==4:break
    if len(c9_vias)==4:break
assert len(c9_vias)>=3,'Insufficient clearance-screened C9 return vias'
print('C9 direct ground vias:',c9_vias,flush=True)
track('/NMOS_DRIVE',p.F_Cu,.2,[(61.2,201.85),(61.175,202)])
track('/NMOS_DRIVE',p.In1_Cu,.2,[(61.2,201.85),(61.2,202.5718)])
# Route only the low-current signals displaced by the reserved power paths.
base=g.masks
def masks(net):
    blocked,vb=base(net)
    for x,y in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)):
        for mask in blocked:g.segment(mask,x,y,x,y,3.36)
        g.segment(vb,x,y,x,y,3.51)
    return blocked,vb
g.masks=masks
results=[{'net':'/5V_PI','ok':g.route('/5V_PI',(74.5,192.5,3),(74.7678,197.2571,2))}]
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'bec_displaced_routes.json').write_text(json.dumps(results,indent=2)+'\n')
print('Added explicit BEC input and return copper',flush=True)
