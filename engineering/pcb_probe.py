import pcbnew
print('Loading board',flush=True)
b=pcbnew.LoadBoard('engineering/baseline/Swayatt_PCB.kicad_pcb')
print('Loaded',len(list(b.GetFootprints())),flush=True)
print('Nets',type(b.GetNetsByName()),flush=True)
for k,v in list(b.GetNetsByName().items())[:2]:print(k,type(v),dir(v)[:20],flush=True)
new=p if False else pcbnew.NETINFO_ITEM(b,'TEST_NET')
print('new',type(new),new.GetNetCode(),flush=True)
