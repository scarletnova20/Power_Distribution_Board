"""Identify the existing routed 5 V indicator without changing copper."""
from pathlib import Path
import sys,shutil,uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one,prop
root=Path('engineering/release42')
backup=root/'before_led_status'
backup.mkdir(exist_ok=True)
for suffix in ('kicad_pcb','kicad_sch','kicad_pro'):
    source=root/('release_candidate.'+suffix)
    if not (backup/source.name).exists():shutil.copy2(source,backup/source.name)
schpath=root/'release_candidate.kicad_sch'
sch=parse(schpath.read_text())
for s in children(sch,'symbol'):
    if prop(s,'Reference')[2]=='D3':
        prop(s,'Value')[2]='GREEN 5V ON'
        prop(s,'Description')[2]='Green 0805 LED; indicates regulated 5V present, not power-good qualification'
for note in children(sch,'text'):
    note[1]=note[1].replace('4-6S NMOS','4S NMOS').replace('40 x 40 mm target','42 x 42 mm target').replace('DJI rail is 12V from external BEC','DJI rail is 9V from external BEC')
one(one(sch,'title_block'),'rev')[1]='WIP-42mm-4S'
schpath.write_text(dump(sch)+'\n')
boardpath=root/'release_candidate.kicad_pcb'
board=parse(boardpath.read_text())
for f in children(board,'footprint'):
    if prop(f,'Reference')[2]=='D3':prop(f,'Value')[2]='GREEN 5V ON'
for item in children(board,'gr_text'):
    if '40 x 40 mm TARGET' in item[1]:item[1]='42 x 42 mm - ENGINEERING CANDIDATE\nNOT FOR FABRICATION'
if not any(t[1]=='5V ON' for t in children(board,'gr_text')):
    board.append(parse('(gr_text "5V ON" (at 70.4 229.7 0) (layer "F.SilkS") (uuid "'+str(uuid.uuid4())+'") (effects (font (size 0.8 0.8) (thickness 0.12))))'))
boardpath.write_text(dump(board)+'\n')
print('Labeled existing D3/R13 status indicator; original saved in before_led_status')
