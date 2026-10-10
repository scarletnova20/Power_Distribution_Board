from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import pymupdf
for src in Path('engineering/release42/copper_review').glob('*.svg'):
    d=pymupdf.open(str(src));page=d[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1600/page.rect.width,1600/page.rect.width)).save(str(src.with_suffix('.png')))
print('Rendered copper layer review images')
