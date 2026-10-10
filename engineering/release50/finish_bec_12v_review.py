"""Refresh revision notes and raster previews before visual review/packaging."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent / 'vendor'))
import pymupdf
out = root / 'lioncircuits_review'
path = out / 'README.md'
text = path.read_text(encoding='utf-8').replace('reports 908 findings: 199 annular-ring, 199 track-width and 510', 'reports 901 findings: 199 annular-ring, 199 track-width and 503')
note = ('\n## External BEC revision — 2026-09-11\n\n'
        'User confirmed external BEC modules are retained. J4/J8 servo and J10/J11 DJI\n'
        'interfaces now specify 12 V; the 5 V interfaces are unchanged. Set/select the\n'
        'external modules for the specified output; this PCB does not set their voltage.\n'
        'Exact BEC and load models, load voltage compatibility and output currents\n'
        'remain unverified. Full netlist comparison preserves every connection, with\n'
        'only the two rail names changed. Copper, stackup and holes are unchanged.\n')
if '## External BEC revision' not in text:
    text += note
path.write_text(text, encoding='utf-8')
path = out / 'SUPPLIER_REVIEW_REQUEST.txt'
text = path.read_text(encoding='utf-8')
note = ('\nRevision 2026-09-11: external BEC interfaces are 5 V and 12 V. Servo J4/J8\n'
        'and DJI J10/J11 previously marked 9 V are now 12 V; copper, stackup and\n'
        'drills are unchanged. Please use this regenerated review package.\n')
if 'external BEC interfaces are 5 V and 12 V' not in text:
    text += note
path.write_text(text, encoding='utf-8')
path = root / 'CONTINUATION.md'
text = path.read_text(encoding='utf-8')
text = text.replace('Previous native files and review ZIPs are in before_bec_12v/.',
    'Fresh checks: ERC 0, unconnected 0, all 52 + 9 checks pass; DRC 901\n'
    '(199 annular, 199 width, 503 clearance), zero silk/text findings.\n'
    'Full netlist comparison and copper/stackup/drill comparison pass.\n'
    'Previous native files and review ZIPs are in before_bec_12v/.')
path.write_text(text, encoding='utf-8')
names = ['front', 'back', 'gerber_top_silk', 'gerber_bottom_silk',
         'component_locator_front', 'component_locator_back', 'assembly_front', 'assembly_back']
sheet = pymupdf.open()
page = sheet.new_page(width=1600, height=2400)
for index, name in enumerate(names):
    path = out / 'previews' / (name + '.svg')
    doc = pymupdf.open(str(path))
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(1700/doc[0].rect.width, 1700/doc[0].rect.width))
    pix.save(str(path.with_suffix('.png')))
    x = (index % 2) * 800
    y = (index // 2) * 600
    page.insert_text((x + 12, y + 18), name, fontsize=14)
    page.insert_image(pymupdf.Rect(x+10, y+25, x+790, y+590), pixmap=pix)
page.get_pixmap().save(str(root / 'bec_12v_visual_review.png'))
print('Revision notes and previews refreshed.')
