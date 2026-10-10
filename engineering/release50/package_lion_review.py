"""Package reviewed outputs with per-file hashes; release remains on hold."""
from pathlib import Path
import hashlib,json,zipfile,shutil
root=Path(__file__).resolve().parent;out=root/'lioncircuits_review'
digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
boardhash=digest(root/'PDB_50A.kicad_pcb')
for name in ('verification.json','export_verification.json'):
    assert json.loads((out/'checks'/name).read_text())['board_sha256']==boardhash
assert digest(out/'source/PDB_50A.kicad_pcb')==boardhash
for ext in ('kicad_sch','kicad_pro','kicad_dru'):
    assert digest(root/f'PDB_50A.{ext}')==digest(out/'source'/f'PDB_50A.{ext}')
visual=dict(board_sha256=boardhash,date='2026-09-11',
    reviewed=['gerber_top_silk','gerber_bottom_silk',
              'front','back','component_locator_front','component_locator_back'],
    findings=['Layer registration, outline and hole placement agree with native board.',
              'Copper/stackup and holes are independently unchanged from the previously reviewed revision; via-in-pad requires documented fill/cap.',
              'Fine-pitch gaps and via annuli remain incompatible with the published LionCircuits screen.',
              '58 silk references and 20 assembly-only references; indexed component locators supplement dense assembly drawings.',
              'Gerbonara warns about KiCad G90 after Excellon header; parsed absolute coordinates match the native design.'],
    fabrication_release=False)
(out/'checks/visual_review.json').write_text(json.dumps(visual,indent=2)+'\n')
status=dict(board_sha256=boardhash,fabricator='LionCircuits',
    fabrication_files_generated=True,independent_export_checks_pass=True,electrical_connectivity_pass=True,
    lioncircuits_published_rules_pass=False,vendor_custom_process_accepted=False,
    exact_assembly_BOM_released=False,fabrication_ready=False,qualified_50A_rating=False,
    next_required_input='LionCircuits custom process acceptance or accepted rule deck/stackup for redesign; see prepared supplier request')
(out/'RELEASE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
shutil.copy2(root/'label_placement.json',out/'checks/label_placement.json')
upload=root/'PDB_50A_LionCircuits_GERBERS_REVIEW_ONLY.zip'
with zipfile.ZipFile(upload,'w',zipfile.ZIP_DEFLATED) as z:
    for folder,pattern in [('gerbers','*'),('drill','*.drl')]:
        for path in sorted((out/folder).glob(pattern)):
            if path.is_file():z.write(path,path.name)
    z.write(out/'UPLOAD_FOR_REVIEW.txt','REVIEW_ONLY.txt')
with zipfile.ZipFile(upload) as z:
    assert z.testzip() is None
    for folder,pattern in [('gerbers','*'),('drill','*.drl')]:
        for path in (out/folder).glob(pattern):
            if path.is_file():assert hashlib.sha256(z.read(path.name)).hexdigest()==digest(path)
(out/'checks/upload_archive_verification.json').write_text(json.dumps(dict(archive=upload.name,sha256=digest(upload),board_sha256=boardhash,all_file_hashes_verified=True,fabrication_ready=False),indent=2)+'\n')
manifest={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
(out/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=root/'PDB_50A_LionCircuits_REVIEW_HOLD.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if p.is_file():z.write(p,str(p.relative_to(out)).replace('\\','/'))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,expected in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==expected,name
(root/'lioncircuits_archive_verification.json').write_text(json.dumps(dict(archive=archive.name,sha256=digest(archive),
    entries=len(manifest)+1,all_file_hashes_verified=True,board_sha256=boardhash,fabrication_ready=False),indent=2)+'\n')
print(archive,archive.stat().st_size,'bytes; archive contents verified')
