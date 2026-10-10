from pathlib import Path
import json
from sexpr import parse,one,children,Atom,dump
def n(k,*v):return [Atom(k),*v]
board=Path('Swayatt_PCB.kicad_pcb')
s=parse(board.read_text(encoding='utf-8'))
setup=one(s,'setup');old=one(setup,'stackup');setup.remove(old)
stack=n('stackup')
for layer,typ,t in [('F.SilkS','Top Silk Screen',None),('F.Paste','Top Solder Paste',None),
 ('F.Mask','Top Solder Mask',.01),('F.Cu','copper',.07),('dielectric 1','prepreg',.2),
 ('In1.Cu','copper',.035),('dielectric 2','core',.97),('In2.Cu','copper',.035),
 ('dielectric 3','prepreg',.2),('B.Cu','copper',.07),('B.Mask','Bottom Solder Mask',.01),
 ('B.Paste','Bottom Solder Paste',None),('B.SilkS','Bottom Silk Screen',None)]:
    entry=n('layer',layer,n('type',typ))
    if t is not None:entry.append(n('thickness',Atom(str(t))))
    if layer.startswith('dielectric'):entry.extend([n('material','FR4'),n('epsilon_r',Atom('4.5')),n('loss_tangent',Atom('0.02'))])
    stack.append(entry)
stack.extend([n('copper_finish','ENIG'),n('dielectric_constraints',Atom('no'))])
setup.insert(1,stack)
board.write_text(dump(s)+'\n',encoding='utf-8')
project=Path('Swayatt_PCB.kicad_pro');data=json.loads(project.read_text())
# Enable all inherited ignored checks; irrelevant rule types remain harmless.
for name,severity in data['board']['design_settings']['rule_severities'].items():
    if severity=='ignore':data['board']['design_settings']['rule_severities'][name]='warning'
assert not data['board']['design_settings']['drc_exclusions']
project.write_text(json.dumps(data,indent=2)+'\n')
print('Four-layer 1.6mm stackup; 70/35/35/70um copper. All inherited ignored DRC checks enabled.')
