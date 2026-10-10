import pcbnew as p
import json
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
print('API', [x for x in dir(p) if 'SPECCTRA' in x],flush=True)
rows=[]
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
    box=f.GetBoundingBox(False,False)
    rows.append({'ref':f.GetReference(),'fp':str(f.GetFPID()),'xy':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],
      'size':[round(p.ToMM(box.GetWidth()),2),round(p.ToMM(box.GetHeight()),2)],
      'pads':[[q.GetNumber(),round(p.ToMM(q.GetPosition().x-f.GetPosition().x),3),round(p.ToMM(q.GetPosition().y-f.GetPosition().y),3),q.GetNetname()] for q in f.Pads()]})
print(json.dumps(rows,indent=None),flush=True)
print('layers',b.GetCopperLayerCount(),flush=True)
print('settings', [x for x in dir(b.GetDesignSettings()) if 'Stack' in x or 'Copper' in x],flush=True)
