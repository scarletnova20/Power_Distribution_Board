from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import pymupdf
for name in ('lm5576','lm74502','isc027n10nm6'):
    src=Path('engineering/release42/lm5576.pdf') if name=='lm5576' else Path('engineering/datasheets')/(name+'.pdf')
    doc=pymupdf.open(str(src))
    out=Path('engineering/release42')/(name+'.txt')
    out.write_text('\n'.join('\nPAGE '+str(i+1)+'\n'+page.get_text() for i,page in enumerate(doc)),encoding='utf-8')
print('Extracted local datasheets')
