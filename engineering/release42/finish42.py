from pathlib import Path
import pcbnew as p
import grid_helpers as g
board=Path('Swayatt_PCB_42x42.kicad_pcb')
backup=Path('engineering/release42/before_grid.kicad_pcb')
if not backup.exists():backup.write_bytes(board.read_bytes())
b=p.LoadBoard(str(board));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
# Restore top-edge trace to a legal midpoint between board edge and the Vin via.
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):continue
    if t.GetNetname()=='/PGND':
        for get,setter in ((t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)):
            v=get()
            if v.y<p.FromMM(189.7):setter(p.VECTOR2I(v.x,p.FromMM(189.602)))
base_masks=g.masks
def masks(net):
    blocked,vb=base_masks(net)
    for x,y in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)):
        for layer in blocked:g.segment(layer,x,y,x,y,3.36)
        g.segment(vb,x,y,x,y,3.51)
    return blocked,vb
g.masks=masks
jobs=[('/DIG_SENSE_N',(82.1,214.5,0),(84.8,208.05,0)),
      ('/RT',(88.47,212.22,3),(96.,213.675,3)),
      ('/COMP_RC',(89.325,201.,3),(94.,215.275,3))]
results=[g.route(*job) for job in jobs]
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(board),b)
print('Results',results,flush=True)
