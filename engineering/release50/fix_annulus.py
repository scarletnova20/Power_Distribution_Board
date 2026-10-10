"""Raise annulus on vias that cannot grow, by shrinking the drill instead.

Shrinking the drill costs barrel cross-section, so it is applied ONLY to
signal-net vias. Power vias keep the 0.30 mm barrel for current capacity.
"""
import sys; sys.path.insert(0,'../vendor')
import pcbnew
TARGET=0.127                       # 5 mil annular ring
POWER={'/Vin','/VCC','/PGND','/BAT_FUSED','/GNDA'}
b=pcbnew.LoadBoard('PDB_50A.kicad_pcb')
fixed=[];kept=[]
for t in b.GetTracks():
    if not isinstance(t,pcbnew.PCB_VIA): continue
    w=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)); d=pcbnew.ToMM(t.GetDrillValue())
    ann=(w-d)/2
    if ann>=TARGET-1e-9: continue
    net=t.GetNetname()
    if net in POWER:
        kept.append((net,round(w,4),round(d,3),round(ann,4))); continue
    nd=round(w-2*TARGET-0.006,3)          # drill that yields the target ring
    nd=max(min(nd,0.25),0.20)             # keep within 0.20-0.25 mm
    t.SetDrill(pcbnew.FromMM(nd))
    fixed.append((net,round(w,4),round(d,3),nd,round((w-nd)/2,4)))
print('signal vias re-drilled (net, pad, old drill, new drill, new annulus):')
for r in fixed: print('  ',r)
if kept: print('POWER vias left below target (barrel preserved):'); [print('  ',r) for r in kept]
f=pcbnew.ZONE_FILLER(b); f.Fill(b.Zones()); b.Save('PDB_50A.kicad_pcb')
ann=[(pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))-pcbnew.ToMM(t.GetDrillValue()))/2 for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
dr=sorted({round(pcbnew.ToMM(t.GetDrillValue()),3) for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)})
print(f'saved. min annulus={min(ann):.4f} mm  drills used={dr}')
