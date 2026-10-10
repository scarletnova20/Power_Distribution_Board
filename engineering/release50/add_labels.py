"""Place all reference fields on accessible silk without modifying copper."""
from pathlib import Path
import sys,json,shutil,math
import numpy as np
import pcbnew as p
root=Path(__file__).resolve().parent
backup=root/'before_labels';backup.mkdir(exist_ok=True)
for name in ('PDB_50A.kicad_pcb','PDB_50A.kicad_pro','verification.json','drc.json'):
    if not (backup/name).exists():shutil.copy2(root/name,backup/name)
b=p.LoadBoard(str(root/'PDB_50A.kicad_pcb'))
# Preserve the current board on reruns; replace only our own team legend.
for item in list(b.GetDrawings()):
    if isinstance(item,p.PCB_TEXT) and item.GetText()=='Team_RotorFPV':b.Remove(item)
fs={f.GetReference():f for f in b.GetFootprints()}
def box(item):
    bb=item.GetBoundingBox()
    return np.array([p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
def inflate(a,d):return a+np.array([-d,-d,d,d])
static={p.F_SilkS:[],p.B_SilkS:[]};bodies={}
for ref,f in fs.items():
    bb=f.GetBoundingBox(False,False)
    body=np.array([p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
    side=p.F_SilkS if f.GetLayer()==p.F_Cu else p.B_SilkS
    fab=p.F_Fab if side==p.F_SilkS else p.B_Fab
    shapes=[box(g) for g in f.GraphicalItems() if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==fab]
    if shapes and not ref.startswith('H'):
        body=np.array([min(a[0] for a in shapes),min(a[1] for a in shapes),max(a[2] for a in shapes),max(a[3] for a in shapes)])
    bodies[ref]=body
    # Wire lands, net ties and testpoints have no component body hiding text.
    if ref not in ('J1','J12','BEC1','J3','J4','J10','J11') and not ref.startswith(('NT','TP')):
        static[side].append(inflate(body,.1))
    if ref.startswith('H'):static[p.B_SilkS].append(inflate(body,.025))
    for q in f.Pads():
        for silk,mask in [(p.F_SilkS,p.F_Mask),(p.B_SilkS,p.B_Mask)]:
            if q.GetLayerSet().Contains(mask):static[silk].append(inflate(box(q),.18))
    for item in f.GraphicalItems():
        if item.GetLayer() in static:static[item.GetLayer()].append(inflate(box(item),.16))
    f.Reference().SetVisible(False)
for item in b.GetDrawings():
    if item.GetLayer() in static:static[item.GetLayer()].append(inflate(box(item),.16))
grid=np.stack(np.meshgrid(np.arange(59.4,100.61,.15),np.arange(189.4,230.61,.15)),axis=-1).reshape(-1,2)
def setup(text,side,size=.8):
    text.SetLayer(side);text.SetVisible(True);text.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size)))
    text.SetTextThickness(p.FromMM(.16));text.SetKeepUpright(False);text.SetMirrored(side==p.B_SilkS)
def candidates(text,side,center,body,maxdistance=4.5):
    allrows=[]
    for angle in (0,90):
        text.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));text.SetPosition(p.VECTOR2I(0,0))
        relative=box(text)
        boxes=np.tile(relative,(len(grid),1))+grid[:,[0,1,0,1]]
        valid=(boxes[:,0]>=59.18)&(boxes[:,1]>=189.18)&(boxes[:,2]<=100.82)&(boxes[:,3]<=230.82)
        distance=np.linalg.norm(grid-center,axis=1);valid &= distance<maxdistance
        for obstacle in static[side]:
            overlap=(boxes[:,0]<obstacle[2])&(boxes[:,2]>obstacle[0])&(boxes[:,1]<obstacle[3])&(boxes[:,3]>obstacle[1])
            valid &= ~overlap
        ix=np.flatnonzero(valid)
        gap=np.linalg.norm(np.maximum(np.maximum(body[:2]-grid[ix],grid[ix]-body[2:]),0),axis=1)
        score=distance[ix]+2*gap+(.35 if angle else 0)
        allrows.extend(zip(score,grid[ix,0],grid[ix,1],np.full(len(ix),angle),boxes[ix]))
    return sorted(allrows,key=lambda x:x[0])
team=p.PCB_TEXT(b);team.SetText('Team_RotorFPV');setup(team,p.F_SilkS,1.)
choices=candidates(team,p.F_SilkS,np.array([89.,197.8]),np.array([83.,197.,99.,199.]),20.)
assert choices,'No space for team name'
choice=next((q for q in choices if q[3]==0),choices[0])
_,x,y,angle,bb=choice;team.SetPosition(p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y))));team.SetTextAngle(p.EDA_ANGLE(float(angle),p.DEGREES_T));b.Add(team)
static[p.F_SilkS].append(inflate(bb,.18))
print('Team name',x,y,angle,flush=True)
pools={};sides={}
for ref,f in fs.items():
    side=p.F_SilkS if f.GetLayer()==p.F_Cu else p.B_SilkS;sides[ref]=side
    text=f.Reference();setup(text,side)
    center=np.array([p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)])
    pools[ref]=candidates(text,side,center,bodies[ref])
    text.SetVisible(False)
    print(ref,'candidates',len(pools[ref]),flush=True)
rng=np.random.default_rng(42);best=None
for attempt in range(100):
    placed={};occupied={p.F_SilkS:[],p.B_SilkS:[]};cost=0
    order=sorted((ref for ref in pools if pools[ref]),key=lambda ref:len([q for q in pools[ref] if q[0]<pools[ref][0][0]+2])*(rng.uniform(.5,1.5) if attempt else 1))
    for ref in order:
        side=sides[ref]
        for candidate in pools[ref]:
            score,x,y,angle,bb=candidate
            if any(bb[0]<o[2] and bb[2]>o[0] and bb[1]<o[3] and bb[3]>o[1] for o in occupied[side]):continue
            placed[ref]=candidate;occupied[side].append(inflate(bb,.18));cost+=score;break
    if best is None or (-len(placed),cost)<(-len(best[1]),best[0]):best=(cost,placed)
assert best,'Unable to place labels'
report=[]
for ref,(_,x,y,angle,bb) in best[1].items():
    t=fs[ref].Reference();setup(t,sides[ref]);t.SetPosition(p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y))));t.SetTextAngle(p.EDA_ANGLE(float(angle),p.DEGREES_T))
    report.append(dict(reference=ref,x_mm=round(float(x),4),y_mm=round(float(y),4),angle_deg=int(angle),side=b.GetLayerName(sides[ref])))
omitted=sorted(set(fs)-set(best[1]))
for ref in omitted:
    f=fs[ref];t=f.Reference()
    setup(t,p.F_Fab if f.GetLayer()==p.F_Cu else p.B_Fab)
    t.SetMirrored(f.GetLayer()==p.B_Cu);t.SetPosition(f.GetPosition());t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
p.SaveBoard(str(root/'PDB_50A.kicad_pcb'),b)
(root/'label_placement.json').write_text(json.dumps(dict(team_name='Team_RotorFPV',reference_height_mm=.8,stroke_mm=.16,maximum_silk_reference_distance_mm=4.5,references=report,assembly_only_references=omitted),indent=2)+'\n')
print('Placed',len(report),'silk references;',len(omitted),'on assembly layer:',omitted,flush=True)
