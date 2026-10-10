"""Reproducible feature inventory and LionCircuits custom 2 oz rule setup.

No copper geometry is modified. Reported pad gaps are for aligned rectangular
pad bounding boxes; KiCad DRC supplies the complete routed-copper check.
"""
from pathlib import Path
import sys,json,math,collections,hashlib,csv
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent))
from sexpr import parse,dump,children,one,prop,Atom
target=root/'PDB_50A.kicad_pcb'
raw=parse(target.read_text(encoding='utf-8-sig'))
out=root/'lioncircuits_review';out.mkdir(exist_ok=True)
for parent in [raw]+children(raw,'footprint'):
    for item in parent:
        if not isinstance(item,list):continue
        layer=one(item,'layer')
        if not layer or layer[1] not in ('F.SilkS','B.SilkS'):continue
        stroke=one(item,'stroke')
        if stroke is not None and float(one(stroke,'width')[1])<.16:one(stroke,'width')[1]=Atom('.16')
        effects=one(item,'effects')
        if effects is not None:
            font=one(effects,'font');one(font,'thickness')[1]=Atom('.16')
one(one(raw,'setup'),'solder_mask_min_width')[1]=Atom('.16')
target.write_text(dump(raw)+'\n',encoding='utf-8')
settings=root/'PDB_50A.kicad_pro';pro=json.loads(settings.read_text(encoding='utf-8-sig'))
rules=pro['board']['design_settings']['rules']
rules.update(min_clearance=.254,min_track_width=.254,min_via_annular_width=.1524,
             min_hole_clearance=.254,min_hole_to_hole=.254,min_silk_clearance=.1524,
             min_text_thickness=.1524,min_text_height=.8)
pro['board']['design_settings']['defaults'].update(silk_line_width=.16,silk_text_thickness=.16)
settings.write_text(json.dumps(pro,indent=2)+'\n',encoding='utf-8')
(root/'PDB_50A.kicad_dru').write_text('''(version 1)
# LionCircuits Custom 2oz capability screen, 2026-09-10.
# https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb
# Preserve stricter existing component-hole rules; no exclusions.
(rule "LionCircuits 2oz width" (constraint track_width (min 0.254mm)))
(rule "LionCircuits 2oz spacing" (constraint clearance (min 0.254mm)))
(rule "PTH component annulus" (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'") (constraint annular_width (min 0.254mm)))
(rule "PTH to other copper" (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'") (constraint hole_clearance (min 0.30mm)))
(rule "Component hole spacing" (condition "A.Type == 'Pad' && B.Type == 'Pad'") (constraint hole_to_hole (min 0.45mm)))
''',encoding='utf-8')
reqpath=root/'requirements.json';req=json.loads(reqpath.read_text())
req.update(fabricator='LionCircuits',fabricator_service='Custom; acceptance pending',
           process_candidate='LionCircuits custom four-layer 2oz all layers, 1.6mm ENIG, filled/capped vias; standard 10mil rules NOT MET',
           battery_topology='4S2P Li-ion; user reconfirmed 2026-09-10')
req['qualification']['A_fabrication_ready']=False
reqpath.write_text(json.dumps(req,indent=2)+'\n')
tracks=[];vias=[];gaps=[];pads=[]
for t in children(raw,'segment'):
    width=float(one(t,'width')[1]);a=list(map(float,one(t,'start')[1:]));b=list(map(float,one(t,'end')[1:]))
    if width<.254-1e-9:tracks.append(dict(uuid=one(t,'uuid')[1],net=one(t,'net')[1],layer=one(t,'layer')[1],width_mm=width,length_mm=math.dist(a,b),start=a,end=b))
for v in children(raw,'via'):
    x,y=map(float,one(v,'at')[1:3]);diam=float(one(v,'size')[1]);drill=float(one(v,'drill')[1])
    vias.append(dict(uuid=one(v,'uuid')[1],x_mm=x,y_mm=y,diameter_mm=diam,drill_mm=drill,annulus_mm=round((diam-drill)/2,6),net=one(v,'net')[1],fill='RESIN FILL AND COPPER CAP BOTH SIDES; no electrical credit for resin'))
for f in children(raw,'footprint'):
    ref=prop(f,'Reference')[2];fpads=children(f,'pad');layer=one(f,'layer')[1]
    at=one(f,'at');fx,fy=map(float,at[1:3]);ang=math.radians(float(at[3]) if len(at)>3 else 0)
    for q in fpads:
        xy=list(map(float,one(q,'at')[1:3]));net=one(q,'net')
        pads.append(dict(reference=ref,pin=q[1],net=net[1] if net else '',side=layer,x_mm=round(fx+xy[0]*math.cos(ang)+xy[1]*math.sin(ang),6),y_mm=round(fy-xy[0]*math.sin(ang)+xy[1]*math.cos(ang),6),kind=q[2],size_mm=list(map(float,one(q,'size')[1:]))))
    for i,a in enumerate(fpads):
        if a[2]!='smd':continue
        for b in fpads[i+1:]:
            if b[2]!='smd':continue
            an,bn=one(a,'net'),one(b,'net')
            if not an or not bn or an[1]==bn[1]:continue
            ax,ay=map(float,one(a,'at')[1:3]);bx,by=map(float,one(b,'at')[1:3])
            aw,ah=map(float,one(a,'size')[1:]);bw,bh=map(float,one(b,'size')[1:])
            # Only aligned pairs: local pad coordinates are before footprint rotation.
            gap=None
            if abs(ax-bx)<1e-8:gap=abs(ay-by)-(ah+bh)/2
            elif abs(ay-by)<1e-8:gap=abs(ax-bx)-(aw+bw)/2
            if gap is not None and 0<gap<.254-1e-8:gaps.append(dict(reference=ref,pads=[a[1],b[1]],gap_mm=round(gap,6),footprint=f[1]))
ann=[v for v in vias if v['annulus_mm']<.1524-1e-9]
report=dict(board_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),fabricator='LionCircuits',service='Custom, 2oz',
    source='https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb',accessed='2026-09-10',
    rule_note='Use exact 6mil=0.1524mm rather than rounded 0.152mm; same for 10mil=0.254mm.',
    short_width_segments=len(tracks),short_width_by_layer=dict(collections.Counter(t['layer'] for t in tracks)),
    total_vias=len(vias),undersize_via_annuli=len(ann),minimum_annulus_mm=min(v['annulus_mm'] for v in vias),
    aligned_fine_pitch_pad_gaps=gaps,via_drill_inventory=dict(collections.Counter(str(v['drill_mm']) for v in vias)),
    unverified_process_features=['Filled/capped via-in-pad availability','Guaranteed minimum finished copper and via barrel plating','Accepted 2oz stackup'],
    manufacturing_release=False)
(out/'feature_audit.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'undersize_tracks.json').write_text(json.dumps(tracks,indent=2)+'\n')
for name,rows in [('via_fill_schedule.csv',vias),('undersize_via_annuli.csv',ann),('pad_coordinates.csv',pads)]:
    with (out/name).open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps(report,indent=2),flush=True)
