import importlib.util
print({n:bool(importlib.util.find_spec(n)) for n in ('numpy','scipy','shapely')},flush=True)
import pcbnew as p
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
z=next(iter(b.Zones()))
polys=z.GetFilledPolysList(z.GetLayer())
print([n for n in dir(polys) if any(s in n for s in ['Contain','Outline','Hole','Vertex'])],flush=True)
print('Contains',polys.Contains.__doc__,flush=True)
