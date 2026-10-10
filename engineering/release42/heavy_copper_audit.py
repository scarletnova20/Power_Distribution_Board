"""Read-only track-width screen against published 4 oz process limits."""
from pathlib import Path
import sys,json,hashlib
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,children,one
root=Path(__file__).resolve().parent
board=root/'release_candidate.kicad_pcb'
raw=parse(board.read_text())
counts=Counter()
narrow=Counter()
for track in children(raw,'segment'):
    layer=one(track,'layer')[1];width=float(one(track,'width')[1])
    counts[(layer,width)]+=1
    if width<.3302-1e-9:narrow[layer]+=1
report={'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),
        'source':'https://www.pcbway.com/pcb_prototype/Thick_Copper_PCBs.html',
        'published_4oz_minimum_track_and_spacing_mm':.3302,
        'tracks_below_published_width_by_layer':dict(narrow),
        'track_widths':[{'layer':k[0],'width_mm':k[1],'count':v} for k,v in sorted(counts.items())],
        'scope':'Width-only screen; pad spacing, copper necks, drill and stackup acceptance still need process review'}
(root/'heavy_copper_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
