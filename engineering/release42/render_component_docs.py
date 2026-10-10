from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import pymupdf
for name,pages in [('panasonic_land_patterns',[0]),('bsc016n06ns',[10,11,12])]:
    src=Path('engineering/release42')/(name+'.pdf')
    if src.stat().st_size==0:continue
    d=pymupdf.open(str(src))
    for i in pages:
        d[i].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(str(src.with_name(name+'_'+str(i+1)+'.png')))
print('Rendered available component drawings')
