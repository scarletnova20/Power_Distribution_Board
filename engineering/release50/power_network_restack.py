"""DC screen of positive copper, four MOSFETs, two shunts and ground return.

Ideal equipotential device pads/via annuli. Explicit geometry and solver
limitations are emitted; results are not thermal or production qualification.
"""
from pathlib import Path
import os,sys,json,math,hashlib,argparse
os.environ['OPENBLAS_NUM_THREADS']='1'
base=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(base/'vendor'));sys.path.insert(0,str(base))
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
import pyamg,pcbnew as p
from sexpr import parse,children,one
ap=argparse.ArgumentParser();ap.add_argument('--mesh',type=float,default=.2)
ap.add_argument('--copper',type=float,default=70);ap.add_argument('--plating',type=float,default=18)
ap.add_argument('--temperature',type=float,default=125);ap.add_argument('--mosfet-mohm',type=float,default=5.4)
ap.add_argument('--copper-layers',default='',help='per-layer um F.Cu,In1,In2,B.Cu; overrides --copper for sheet conductance')
ap.add_argument('--tag',default='');args=ap.parse_args()
root=Path(__file__).resolve().parent;target=root/'PDB_50A.kicad_pcb'
b=p.LoadBoard(str(target));raw=parse(target.read_text())
nets=['/BAT_FUSED','/VCC','/Vin','/PGND'];layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
names=['F.Cu','In1.Cu','In2.Cu','B.Cu']
sx=np.arange(59+args.mesh/2,101,args.mesh);sy=np.arange(189+args.mesh/2,231,args.mesh)
X,Y=np.meshgrid(sx,sy);shape=X.shape
mask=np.zeros((4,4,*shape),bool)
def polygon(points):
    result=np.zeros(shape,bool)
    for j,y in enumerate(sy):
        hits=sorted(ax+(y-ay)*(bx-ax)/(by-ay) for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]) if (ay>y)!=(by>y))
        for a,c in zip(hits[::2],hits[1::2]):result[j]|=(sx>=a)&(sx<c)
    return result
for zone in children(raw,'zone'):
    net=one(zone,'net')
    if net is None or net[1] not in nets:continue
    for f in children(zone,'filled_polygon'):
        name=one(f,'layer')[1]
        if name in names:mask[nets.index(net[1]),names.index(name)]|=polygon([tuple(map(float,q[1:3])) for q in children(one(f,'pts'),'xy')])
pad_masks={};pad_layers={};pad_nets={};holes=np.zeros(shape,bool)
for f in b.GetFootprints():
    for q in f.Pads():
        x,y=p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)
        if q.GetDrillSize().x:
            # All drilled pads in this board are circular; do not assume slots.
            assert q.GetDrillSize().x==q.GetDrillSize().y
            holes|=(X-x)**2+(Y-y)**2<(p.ToMM(q.GetDrillSize().x)/2)**2
        if q.GetNetname() not in nets:continue
        n=nets.index(q.GetNetname());w,h=p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)
        theta=math.radians(q.GetOrientationDegrees());dx=X-x;dy=Y-y
        u=abs(dx*math.cos(theta)-dy*math.sin(theta));v=abs(dx*math.sin(theta)+dy*math.cos(theta))
        if q.GetShape()==p.PAD_SHAPE_CIRCLE:area=dx*dx+dy*dy<=(w/2)**2
        elif q.GetShape()==p.PAD_SHAPE_ROUNDRECT:
            r=p.ToMM(q.GetRoundRectCornerRadius());area=(np.maximum(u-w/2+r,0)**2+np.maximum(v-h/2+r,0)**2<=r*r)
        else:area=(u<=w/2)&(v<=h/2)
        key=f.GetReference()+'.'+q.GetNumber();ks=[k for k,l in enumerate(layers) if q.GetLayerSet().Contains(l)]
        for k in ks:mask[n,k]|=area
        pad_masks[key]=pad_masks.get(key,np.zeros(shape,bool))|area;pad_layers[key]=ks;pad_nets[key]=n
vias=[]
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):
        x,y=p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y);drill=p.ToMM(t.GetDrillValue())
        holes|=(X-x)**2+(Y-y)**2<(drill/2)**2
        if t.GetNetname() not in nets:continue
        n=nets.index(t.GetNetname());disk=(X-x)**2+(Y-y)**2<=(p.ToMM(t.GetWidth(p.F_Cu))/2)**2
        mask[n]|=disk;vias.append((n,disk,drill,t.m_Uuid.AsString(),x,y))
    elif t.GetNetname() in nets and t.GetLayer() in layers:
        n=nets.index(t.GetNetname());k=layers.index(t.GetLayer())
        ax,ay=p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y);bx,by=p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)
        dx,dy=bx-ax,by-ay;d=dx*dx+dy*dy
        u=np.clip(((X-ax)*dx+(Y-ay)*dy)/d,0,1) if d else 0
        mask[n,k]|=(X-ax-u*dx)**2+(Y-ay-u*dy)**2<=(p.ToMM(t.GetWidth())/2)**2
mask&=~holes
ids=np.full(mask.shape,-1,np.int32);ids[mask]=np.arange(mask.sum(),dtype=np.int32)
parent=np.arange(mask.sum(),dtype=np.int32)
def union(values):
    values=np.unique(values[values>=0]);assert len(values),'Mesh missed a contact'
    while not np.array_equal(values,parent[values]):values=np.unique(parent[values])
    parent[values]=values[0];return int(values[0])
contacts={}
for key in ['J1.1','J1.2','J12.1','J12.2']+[f'Q{i}.{pin}' for i in range(1,5) for pin in (2,3)]+[f'R{i}.{pin}' for i in (10,11) for pin in (1,2)]:
    contacts[key]=union(np.concatenate([ids[pad_nets[key],k][pad_masks[key]] for k in pad_layers[key]]))
via_nodes=[]
for n,disk,drill,uid,x,y in vias:
    via_nodes.append(([union(ids[n,k][disk]) for k in range(4)],drill,n,uid,x,y))
while not np.array_equal(parent,parent[parent]):parent=parent[parent]
roots,inverse=np.unique(parent,return_inverse=True);node_count=len(roots)
mapped=np.full(ids.shape,-1,np.int32);mapped[mask]=inverse
contact={k:int(inverse[v]) for k,v in contacts.items()}
rho=1.724e-8*(1+.00393*(args.temperature-20));sheet=args.copper*1e-6/rho
_cl=[float(x) for x in args.copper_layers.split(',')] if args.copper_layers else [args.copper]*4
assert len(_cl)==4,'--copper-layers needs 4 values'
sheet_layers=[t*1e-6/rho for t in _cl]
eu=[];ev=[];eg=[];kind=[]
def edges(a,c,g,label):
    a=np.asarray(a).ravel();c=np.asarray(c).ravel();valid=(a>=0)&(c>=0)&(a!=c)
    eu.extend(a[valid]);ev.extend(c[valid]);eg.extend(np.broadcast_to(g,a.shape)[valid]);kind.extend([label]*int(valid.sum()))
for n in range(4):
    for k in range(4):
        for a,c in [(mapped[n,k,:,1:],mapped[n,k,:,:-1]),(mapped[n,k,1:,:],mapped[n,k,:-1,:])]:edges(a,c,sheet_layers[k],'ground_copper' if n==3 else 'positive_copper')
via_edges=[]
for nodes,drill,n,uid,x,y in via_nodes:
    nodes=[int(inverse[v]) for v in nodes]
    area=math.pi*(drill/1000)*args.plating*1e-6
    for k,length in enumerate((.27e-3,.97e-3,.27e-3)):
        start=len(eu);edges([nodes[k]],[nodes[k+1]],area/(rho*length),'ground_vias' if n==3 else 'positive_vias')
        via_edges.append((start,uid,x,y,k,n))
for i in range(1,5):edges([contact[f'Q{i}.3']],[contact[f'Q{i}.2']],1000/args.mosfet_mohm,f'Q{i}')
shunt=.0005*1.01*(1+.0004*(args.temperature-25))
for i in (10,11):edges([contact[f'R{i}.1']],[contact[f'R{i}.2']],1/shunt,f'R{i}')
eu=np.array(eu,np.int32);ev=np.array(ev,np.int32);eg=np.array(eg);kind=np.array(kind)
L=sparse.coo_matrix((np.concatenate((eg,eg,-eg,-eg)),(np.concatenate((eu,ev,eu,ev)),np.concatenate((eu,ev,ev,eu)))),shape=(node_count,node_count)).tocsr()
_,labels=connected_components(L,directed=False)
fixed=np.zeros(node_count,bool);v=np.zeros(node_count)
for key in ('J1.1','J1.2','J12.1','J12.2'):fixed[contact[key]]=True
v[contact['J1.1']]=v[contact['J1.2']]=1
assert labels[contact['J1.1']]==labels[contact['J12.1']],'Positive path disconnected by raster'
assert labels[contact['J1.2']]==labels[contact['J12.2']],'Ground path disconnected by raster'
assert labels[contact['J1.1']]!=labels[contact['J1.2']],'Ground short in network'
active=np.isin(labels,labels[fixed]);free=active&~fixed
A=L[free][:,free];rhs=-(L@v)[free]
print('Power network nodes',node_count,'solved',A.shape[0],flush=True)
ml=pyamg.smoothed_aggregation_solver(A,symmetry='symmetric',max_coarse=100)
v[free]=ml.solve(rhs,tol=1e-10,maxiter=500,accel='cg')
res=float(np.linalg.norm((L@v)[free])/np.linalg.norm(rhs));assert res<1e-8,res
flux=L@v;reports={};scale=np.zeros(node_count)
for name,a,c in [('positive','J1.1','J12.1'),('ground','J1.2','J12.2')]:
    current=float(flux[contact[a]]);balance=abs(current+float(flux[contact[c]]))/current
    assert current>0 and balance<1e-6,(name,current,balance)
    scale[labels==labels[contact[a]]]=50/current
    reports[name]={'resistance_ohm':1/current,'loss_W_at_50A':2500/current,'drop_V_at_50A':50/current,'current_balance_relative':balance}
amps=(v[eu]-v[ev])*eg*scale[eu];watts=amps**2/eg
losses={k:float(watts[kind==k].sum()) for k in sorted(set(kind))}
parts={k:float(amps[kind==k].sum()) for k in ['Q1','Q2','Q3','Q4','R10','R11']}
assert abs(sum(losses.values())-sum(r['loss_W_at_50A'] for r in reports.values()))<1e-5
via_peak=sorted([{'uuid':uid,'xy_mm':[x,y],'segment':k,'net':nets[n],'A':float(abs(amps[i])),'W':float(watts[i])} for i,uid,x,y,k,n in via_edges],key=lambda d:d['A'],reverse=True)[:20]
report={'board_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'parameters':vars(args),'current_A':50,
 'paths':reports,'loss_breakdown_W':losses,'component_current_A':parts,'peak_via_segments':via_peak,
 'combined_loop_resistance_ohm':sum(r['resistance_ohm'] for r in reports.values()),'solver_relative_residual':res,
 'limitations':['DC 50 A ESC-only case; auxiliary branching changes distribution and needs separate load case',
 'All copper at specified uniform temperature; no temperature-rise prediction',
 'RDS hot multiplier is an engineering envelope, not guaranteed hot datasheet maximum',
 'Ideal equipotential solder lands/device terminals/via annuli; solder and joint resistance excluded',
 'Circular drill bores removed; fine raster convergence and via-contact approximation remain',
 'Plating assumed, published average is not guaranteed minimum',
 'Via segment lengths held at inherited stackup screening values; accepted fabrication stackup still needed',
 'No fuse, harness, connector, regulator/BEC conversion loss or thermal coupling in this network'],
 'qualification':False}
out=root/f'power_{args.mesh:g}mm_{(args.copper_layers.replace(chr(44),chr(45)) if args.copper_layers else str(int(args.copper)))}um{args.tag}.json';out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'file':str(out),'paths':reports,'losses':losses,'currents':parts},indent=2),flush=True)
