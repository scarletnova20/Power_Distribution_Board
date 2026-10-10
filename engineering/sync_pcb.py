"""Synchronize connectivity/footprints only. Keep explicit work-in-progress layout.
No autorouting or manufacturing release is implied by this operation.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import pcbnew as p
from sexpr import *

# Continue from the actual board. Loading the baseline here used to discard
# all subsequent placement, tracks and zones every time synchronization ran.
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
sch=parse(Path('Swayatt_PCB.kicad_sch').read_text(encoding='utf-8'))
symbols={prop(s,'Reference')[2]:s for s in children(sch,'symbol') if not prop(s,'Reference')[2].startswith('#')}
r=ET.parse('engineering/corrected_netlist.xml').getroot()
padnets={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in r.find('nets') for n in net}
existing={f.GetReference():f for f in b.GetFootprints()}
oldnets=dict(b.GetNetsByName().items())
netobjs={}
for name in sorted(set(padnets.values())):
    net=oldnets.get(name)
    if not net or net.GetNetCode()<0:
        net=p.NETINFO_ITEM(b,name);b.Add(net)
    netobjs[name]=net
for f in list(b.GetFootprints()):
    ref=f.GetReference()
    if ref not in symbols or one(symbols[ref],'on_board')[1]=='no':b.Remove(f)
libroot=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
added=0
for ref,s in symbols.items():
    if one(s,'on_board')[1]=='no':continue
    fid=prop(s,'Footprint')[2];lib,name=fid.split(':',1)
    old=existing.get(ref)
    if old is not None and str(old.GetFPID())==fid:f=old
    else:
        libpath=Path('Swayatt_Local.pretty').resolve() if lib=='Swayatt_Local' else libroot/(lib+'.pretty')
        f=p.FootprintLoad(str(libpath),name)
        if not f:raise RuntimeError('Cannot load '+fid)
        f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref)
        if old is not None:
            if old.IsFlipped():f.Flip(f.GetPosition(),False)
            f.SetPosition(old.GetPosition());f.SetOrientation(old.GetOrientation());b.Remove(old)
        else:
            f.SetPosition(p.VECTOR2I(p.FromMM(165+(added%5)*18),p.FromMM(35+(added//5)*18)));added+=1
        b.Add(f)
    f.SetValue(prop(s,'Value')[2])
    path=p.KIID_PATH();path.push_back(p.KIID(one(sch,'uuid')[1]));path.push_back(p.KIID(one(s,'uuid')[1]));f.SetPath(path)
    f.SetSheetfile('Swayatt_PCB.kicad_sch');f.SetSheetname('')
    for pad in f.Pads():
        name=padnets.get((ref,pad.GetNumber()))
        if name:pad.SetNet(netobjs[name])
        else:pad.SetNetCode(0)
    f.Value().SetVisible(False)

# Preserve positions and reference locations; only new footprints are parked.
for f in b.GetFootprints():
    if f.GetReference() in ('U1','U3'):f.SetLocalClearance(p.FromMM(.15))

# The 40mm outline is the agreed constraint; existing parts remain parked for redesign.
if not any(d.GetLayer()==p.Edge_Cuts for d in b.GetDrawings()):
    for x1,y1,x2,y2 in [(60,190,100,190),(100,190,100,230),(100,230,60,230),(60,230,60,190)]:
        line=p.PCB_SHAPE();line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(p.VECTOR2I(p.FromMM(x1),p.FromMM(y1)));line.SetEnd(p.VECTOR2I(p.FromMM(x2),p.FromMM(y2)));line.SetLayer(p.Edge_Cuts);line.SetWidth(p.FromMM(.05));b.Add(line)
p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
audit=[]
for f in b.GetFootprints():
    for pad in f.Pads():
        expected=padnets.get((f.GetReference(),pad.GetNumber()))
        if expected and pad.GetNetname()!=expected:audit.append((f.GetReference(),pad.GetNumber(),expected,pad.GetNetname()))
Path('engineering/pcb_sync_audit.json').write_text(json.dumps({'footprints':len(list(b.GetFootprints())),'pad_net_mismatches':audit,'tracks':len(list(b.GetTracks())),'zones':b.GetAreaCount(),'placement_complete':False},indent=2))
print('Synchronized',len(list(b.GetFootprints())),'footprints, mismatches',len(audit),'; placement/routing incomplete',flush=True)
if audit:raise SystemExit(1)
