from pathlib import Path
import pcbnew as p
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb')
backup=Path('engineering/release42/before_repair.kicad_pcb')
if not backup.exists():backup.write_bytes(Path('Swayatt_PCB_42x42.kicad_pcb').read_bytes())
for z in b.Zones():
    if not z.GetIsRuleArea():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
old=p.VECTOR2I(p.FromMM(78.8458),p.FromMM(206.2647))
new=p.VECTOR2I(old.x,p.FromMM(206.20))
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):
        if (t.GetPosition()-old).EuclideanNorm()<p.FromMM(.001):t.SetPosition(new)
        continue
    for get,setter in ((t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)):
        v=get()
        if (v-old).EuclideanNorm()<p.FromMM(.001):setter(new)
        elif t.GetNetname()=='/PGND' and v.y<p.FromMM(189.6):setter(p.VECTOR2I(v.x,p.FromMM(189.65)))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
print('Repaired edge and net-tie clearance; removed floating copper islands',flush=True)
