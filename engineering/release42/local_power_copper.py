"""Reserve regulator power copper and parallel current-transfer vias."""
from pathlib import Path
import pcbnew as p
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_local_power.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
b=p.LoadBoard(str(backup));fs={f.GetReference():f for f in b.GetFootprints()}
nets={q.GetNetname():q.GetNet() for f in fs.values() for q in f.Pads() if q.GetNumber()}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
fs['TP2'].SetPosition(pt(60.8,211.5))
def track(net,layer,width,coords):
    for a,c in zip(coords,coords[1:]):
        t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*c));t.SetLayer(layer);t.SetWidth(p.FromMM(width));t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y):
    v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(nets[net]);v.SetLocked(True);b.Add(v)
def zone(net,coords):
    z=p.ZONE(b);z.SetLayer(p.B_Cu);z.SetNet(nets[net]);z.SetAssignedPriority(20);z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetZoneName('Local buck '+net)
    o=z.Outline();o.NewOutline()
    for x,y in coords:o.Append(p.FromMM(x),p.FromMM(y))
    b.Add(z)
zone('/SW',[(76.5,199.7),(83.2,199.7),(83.2,210),(79,210),(79,218.6),(76.7,218.6),(76.7,211),(75.5,209.5),(75.5,206.5),(76.5,206.5)])
zone('/Vin',[(87.8,201.8),(94,201.8),(94,209.9),(88,209.9),(88,206.0),(87.8,206.0)])
for y in (210.27,210.93):track('/IS_RETURN',p.B_Cu,.3,[(82.53,y),(80.8,y)])
track('/IS_RETURN',p.B_Cu,1,[(80.8,210.27),(80.8,210.93),(80.2,211.53),(80.2,212.9)])
for x in (79.8,80.6):
    for y in (212.5,213.3):via('/IS_RETURN',x,y)
for x,y in ((72.5,205.0),(72.5,205.8),(71.7,204.8)):via('/IS_RETURN',x,y)
track('/IS_RETURN',p.B_Cu,.8,[(71.7,204.8),(72.5,205.4),(73.46,205.28)])
track('/IS_RETURN',p.In2_Cu,.8,[(71.7,204.8),(72.5,205.4)])
track('/IS_RETURN',p.In2_Cu,1.2,[(72.5,205.4),(73.46,212.9),(80.2,212.9)])
for x in (85.6,86.3):
    for y in (204.5,205.3):via('/PGND',x,y)
track('/PGND',p.B_Cu,1.2,[(84.45,198.5),(84.45,203.75),(85.95,203.75)])
# The output capacitor and inductor output sit on the same component side.
track('/out',p.B_Cu,1.2,[(72.67,215),(70.5,215),(68.5375,217.375)])
track('/out',p.B_Cu,1.2,[(72.67,215),(72.67,219.9),(81,219.9)])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
print('Added local switching copper, IS-return current path and capacitor returns',flush=True)
