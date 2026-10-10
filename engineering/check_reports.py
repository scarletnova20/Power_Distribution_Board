import json
from collections import Counter
from pathlib import Path
for name in ('erc','drc'):
    p=Path('engineering')/(name+'.json')
    if not p.exists():continue
    r=json.loads(p.read_text());v=[v for s in r.get('sheets',[]) for v in s['violations']] if name=='erc' else r.get('violations',[])
    print(name,Counter(x['type'] for x in v))
    for typ in sorted(set(x['type'] for x in v)):
        for x in [x for x in v if x['type']==typ][:3]:print(typ,x['description'],[i['description'] for i in x.get('items',[])])
    print('Unconnected',len(r.get('unconnected_items',[])))
