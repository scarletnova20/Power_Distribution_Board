"""Shrink only those vias that still violate clearance, by the exact deficit.

Floor is 0.50 mm (0.10 mm annulus). Reports the worst annulus actually needed
so the required annular-ring capability can be stated honestly.
"""
import sys,json,re,math
sys.path.insert(0,'../vendor')
import pcbnew
MARGIN=0.006   # mm of extra headroom beyond the rule
FLOOR=0.50
drc=json.load(open(sys.argv[1]))
need={}
for v in drc['violations']:
    if v['type']!='clearance': continue
    m=re.search(r'clearance ([0-9.]+) mm; actual ([0-9.]+) mm',v['description'])
    if not m: continue
    req,act=float(m.group(1)),float(m.group(2))
    deficit=req-act+MARGIN
    for it in v['items']:
        if not it.get('description','').startswith('Via'): continue
        p=it['pos']; key=(round(p['x'],3),round(p['y'],3))
        need[key]=max(need.get(key,0.0),deficit)
print('vias needing shrink:',len(need))
b=pcbnew.LoadBoard('PDB_50A.kicad_pcb')
changed=[];floored=[]
for t in b.GetTracks():
    if not isinstance(t,pcbnew.PCB_VIA): continue
    key=(round(pcbnew.ToMM(t.GetPosition().x),3),round(pcbnew.ToMM(t.GetPosition().y),3))
    if key not in need: continue
    cur=pcbnew.ToMM(t.GetWidth()); tgt=cur-2*need[key]
    if tgt<FLOOR: floored.append((key,round(tgt,4))); tgt=FLOOR
    t.SetWidth(pcbnew.FromMM(round(tgt,4)))
    changed.append((key,round(cur,3),round(tgt,4)))
for k,c,t in changed: print(f'   via {k}: {c} -> {t} mm (annulus {(t-0.3)/2:.4f})')
if floored: print('hit 0.50mm floor (cannot shrink further):',floored)
f=pcbnew.ZONE_FILLER(b); f.Fill(b.Zones())
b.Save('PDB_50A.kicad_pcb')
ann=[(pcbnew.ToMM(t.GetWidth())-pcbnew.ToMM(t.GetDrillValue()))/2 for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
print(f'saved. vias={len(ann)} min annulus={min(ann):.4f} mm  max={max(ann):.4f} mm')
