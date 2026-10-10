from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import pymupdf
for side in ('front','back'):
    source=Path('engineering/release42')/(side+'.svg')
    doc=pymupdf.open(str(source));page=doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1600/page.rect.width,1600/page.rect.width)).save(str(source.with_suffix('.png')))
print('Rendered both sides')
