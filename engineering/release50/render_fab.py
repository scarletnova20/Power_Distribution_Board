from pathlib import Path
import sys
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent/'vendor'))
import pymupdf
for arg in sys.argv[1:]:
    source=Path(arg)
    doc=pymupdf.open(str(source)); page=doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1800/page.rect.width,1800/page.rect.width)).save(str(source.with_suffix('.png')))
    print(source.with_suffix('.png'))
