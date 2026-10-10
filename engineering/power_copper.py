"""Add power/return copper and stitched pad arrays; preserve all routed nets."""
import pcbnew as p
from pathlib import Path
import math,json
from sexpr import parse,dump
backup=Path('engineering/before_power.kicad_pcb')
if not backup.exists():backup.write_bytes(Path('Swayatt_PCB.kicad_pcb').read_bytes())
# Re-route signal traces around the power/thermal vias rather than allowing
# a first signal pass to occupy all available exposed-pad via positions.
raw=parse(backup.read_text(encoding='utf-8'))
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0] in ('segment','via','arc'))]
Path('engineering/power_unrouted.kicad_pcb').write_text(dump(raw)+'\n',encoding='utf-8')
b=p.LoadBoard('engineering/power_unrouted.kicad_pcb')
fs={f.GetReference():f for f in b.GetFootprints()}
for ref,x,y,angle in [('C20',13.8,16.8,90),('C21',13.5,13.2,90),('TP1',22,38,0)]:
    fs[ref].SetPosition(p.VECTOR2I(p.FromMM(60+x),p.FromMM(190+y)))
    fs[ref].SetOrientationDegrees(angle)
nets={net.GetNetname():net for net in b.GetNetsByNetcode().values()}
def pos(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def zone(net,layer,x1,y1,x2,y2,priority=0):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['/'+net])
    z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2))
    z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetAssignedPriority(priority)
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName(net+' '+b.GetLayerName(layer))
    outline=z.Outline();outline.NewOutline()
    for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:outline.Append(p.FromMM(x+60),p.FromMM(y+190))
    b.Add(z)
zone('PGND',p.In1_Cu,.4,.4,39.6,39.6)
for layer in (p.F_Cu,p.In2_Cu):
    zone('BAT_FUSED',layer,.4,.4,6,39.6)
    zone('VCC',layer,6.4,.4,18.8,39.6)
    zone('Vin',layer,19.2,.4,39.6,39.6)
zone('PGND',p.F_Cu,29.4,.4,39.6,39.6,5)
zone('GNDA',p.F_Cu,15,23,28,39.6,10)
zone('BAT_FUSED',p.B_Cu,.4,.4,6,39.6)
zone('VCC',p.B_Cu,6.4,.4,18.8,39.6)
zone('PGND',p.B_Cu,19.2,.4,39.6,39.6)

# Conservative clearance guards against existing pads and routed tracks.
def dist_seg(x,y,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay;d=dx*dx+dy*dy
    t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/d)) if d else 0
    return math.hypot(x-ax-t*dx,y-ay-t*dy)
padboxes=[]
for f in fs.values():
    for q in f.Pads():
        if not q.GetLayerSet().Contains(p.F_Cu) and not q.GetLayerSet().Contains(p.B_Cu):continue
        box=q.GetBoundingBox()
        padboxes.append((q.GetNetCode(),p.ToMM(box.GetX()),p.ToMM(box.GetY()),p.ToMM(box.GetRight()),p.ToMM(box.GetBottom())))
traces=[]
for t in b.GetTracks():
    a,c=t.GetStart(),t.GetEnd()
    isvia=isinstance(t,p.PCB_VIA)
    width=t.GetWidth(p.F_Cu) if isvia else t.GetWidth()
    traces.append((t.GetNetCode(),p.ToMM(a.x),p.ToMM(a.y),p.ToMM(c.x),p.ToMM(c.y),p.ToMM(width)/2,isvia))
added=[]
def via(x,y,net):
    radius=.3;clearance=.205
    if not (60.8<=x<=99.2 and 190.8<=y<=229.2):return False
    for nc,x1,y1,x2,y2 in padboxes:
        if nc==net.GetNetCode():continue
        if math.hypot(max(x1-x,0,x-x2),max(y1-y,0,y-y2))<radius+clearance:return False
    for nc,ax,ay,bx,by,r,isvia in traces:
        d=dist_seg(x,y,ax,ay,bx,by)
        if nc!=net.GetNetCode() and d<radius+r+clearance:return False
        if isvia and d<.65:return False
    v=p.PCB_VIA(b);v.SetPosition(pos(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
    v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(net);v.SetLocked(True);b.Add(v)
    traces.append((net.GetNetCode(),x,y,x,y,.3,True));added.append((net.GetNetname(),x,y))
    return True
counts={}
# Reserve the fine-pitch control escapes before the general router works.
for number,x in []:
    q=next(q for q in fs['U1'].Pads() if q.GetNumber()==number)
    start=q.GetPosition();y=p.ToMM(start.y)
    assert via(x,y,q.GetNet()), 'Cannot place U1 escape via '+number
    t=p.PCB_TRACK(b);t.SetStart(start);t.SetEnd(pos(x,y));t.SetWidth(p.FromMM(.2));t.SetLayer(p.B_Cu);t.SetNet(q.GetNet());t.SetLocked(True);b.Add(t)
    traces.append((q.GetNetCode(),p.ToMM(start.x),y,x,y,.1,False))
for ref in ['J1','J12','Q1','Q2','Q3','Q4','R10','R11','U1','J3','J4','J10','BEC1','J11','C1','C2','C9','L1','D1']:
    count=0
    for q in fs[ref].Pads():
        if q.GetNetname() not in ('/PGND','/BAT_FUSED','/VCC','/Vin','/SW','/out','/IS_RETURN'):continue
        box=q.GetBoundingBox();x1,y1=p.ToMM(box.GetX()),p.ToMM(box.GetY());x2,y2=p.ToMM(box.GetRight()),p.ToMM(box.GetBottom())
        # Keep the annulus in the land; filled/capped via-in-pad required for SMT.
        nx=max(1,int((x2-x1-.7)/1)+1);ny=max(1,int((y2-y1-.7)/1)+1)
        if x2-x1<.65 or y2-y1<.65:continue
        for i in range(nx):
            for j in range(ny):
                x=(x1+x2)/2+(i-(nx-1)/2)*1.;y=(y1+y2)/2+(j-(ny-1)/2)*1.
                if q.HitTest(pos(x,y)) and via(x,y,q.GetNet()):count+=1
    counts[ref]=count
b.BuildConnectivity()
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones())
p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
Path('engineering/power_vias.json').write_text(json.dumps({'added':added,'counts':counts},indent=2))
print('Added',len(added),'vias and',len(list(b.Zones())),'zones',counts,flush=True)
