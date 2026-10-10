from pathlib import Path
import json
f=Path('engineering/release42/release_candidate.kicad_pro')
j=json.loads(f.read_text(encoding='utf-8-sig'))
s=j['board']['design_settings']['rule_severities']
changed=[k for k,v in s.items() if v=='ignore']
for k in changed:s[k]='warning'
f.write_text(json.dumps(j,indent=2)+'\n')
print('Enabled previously default-ignored checks:',changed)
