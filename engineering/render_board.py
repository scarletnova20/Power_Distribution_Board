from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import pymupdf
for side in ('front','back'):
    source=Path('engineering')/(side+'.svg')
    doc=pymupdf.open(str(source))
    page=doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1400/page.rect.width,1400/page.rect.height)).save(str(source.with_suffix('.png')))
print('Rendered both board sides')
