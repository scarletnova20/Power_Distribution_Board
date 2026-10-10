"""Finite-difference screening of the actual PGND copper and through-via network.

Not an ampacity or thermal qualification. Raster convergence, plating and ideal
solder-land contacts limit accuracy; no solder, harness or connector resistance.
"""
from pathlib import Path
import os,sys,json,math,hashlib,time
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import pcbnew as p
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,children,one
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
step=float(sys.argv[1]) if len(sys.argv)>1 else .2
copper_um=float(sys.argv[sys.argv.index('--copper-um')+1]) if '--copper-um' in sys.argv else 70.
assert step>0 and copper_um>0
axisx=np.arange(59+step/2,101,step);axisy=np.arange(189+step/2,231,step)
X,Y=np.meshgrid(axisx,axisy);shape=X.shape
mask=np.zeros((4,*shape),bool);names=['F.Cu','In1.Cu','In2.Cu','B.Cu']
raw=parse(target.read_text())
def polygon(points):
    result=np.zeros(shape,bool)
    for j,y in enumerate(axisy):
        intersections=[]
        for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]):
            if (ay>y)!=(by>y):intersections.append(ax+(y-ay)*(bx-ax)/(by-ay))
        intersections.sort()
        for a,c in zip(intersections[::2],intersections[1::2]):result[j]|=(axisx>=a)&(axisx<c)
    return result
for zone in children(raw,'zone'):
    if one(zone,'net') is None or one(zone,'net')[1]!='/PGND':continue
    for filled in children(zone,'filled_polygon'):
        layer=one(filled,'layer')[1]
        if layer not in names:continue
        pts=[tuple(map(float,q[1:3])) for q in children(one(filled,'pts'),'xy')]
        mask[names.index(layer)]|=polygon(pts)
b=p.LoadBoard(str(target));layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
terminals={}
for f in b.GetFootprints():
    for q in f.Pads():
        if q.GetNetname()!='/PGND':continue
        x,y=p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)
        sx,sy=p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)
        angle=math.radians(q.GetOrientationDegrees());dx=X-x;dy=Y-y
        localx=dx*math.cos(angle)-dy*math.sin(angle);localy=dx*math.sin(angle)+dy*math.cos(angle)
        footprint=(abs(localx)<=sx/2)&(abs(localy)<=sy/2)
        for k,l in enumerate(layers):
            if q.GetLayerSet().Contains(l):mask[k]|=footprint
        if f.GetReference() in ('J1','J12'):terminals[f.GetReference()]=footprint
vias=[]
for t in b.GetTracks():
    if t.GetNetname()!='/PGND':continue
    if isinstance(t,p.PCB_VIA):
        x,y=p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)
        r=p.ToMM(t.GetWidth(p.F_Cu))/2
        disk=(X-x)**2+(Y-y)**2<=r*r
        mask|=disk
        i=int(np.argmin(abs(axisx-x)));j=int(np.argmin(abs(axisy-y)))
        mask[:,j,i]=True
        vias.append((j,i,p.ToMM(t.GetDrillValue())))
    else:
        if t.GetLayer() not in layers:continue
        ax,ay=p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)
        bx,by=p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)
        dx,dy=bx-ax,by-ay;d=dx*dx+dy*dy
        u=np.clip(((X-ax)*dx+(Y-ay)*dy)/d,0,1) if d else 0
        mask[layers.index(t.GetLayer())]|=(X-ax-u*dx)**2+(Y-ay-u*dy)**2<=(p.ToMM(t.GetWidth())/2)**2
fixed=~mask;fixed[0]|=terminals['J1']|terminals['J12']
boundary=np.zeros(mask.shape);boundary[0,terminals['J1']]=1
rho=1.724e-8*(1+.00393*(100-20));g_sheet=copper_um*1e-6/rho
gx=(mask[:,:,1:]&mask[:,:,:-1])*g_sheet;gy=(mask[:,1:,:]&mask[:,:-1,:])*g_sheet
reports=[]
for plating in ((20e-6,) if '--single-plating' in sys.argv else (20e-6,25e-6)):
    gz=np.zeros((3,*shape))
    for j,i,drill in vias:
        area=math.pi*(drill/1000)*plating
        for k,length in enumerate((.27e-3,.97e-3,.27e-3)):gz[k,j,i]+=area/(rho*length)
    def laplace(x):
        out=np.zeros_like(x)
        d=gx*(x[:,:,1:]-x[:,:,:-1]);out[:,:,1:]+=d;out[:,:,:-1]-=d
        d=gy*(x[:,1:,:]-x[:,:-1,:]);out[:,1:,:]+=d;out[:,:-1,:]-=d
        d=gz*(x[1:]-x[:-1]);out[1:]+=d;out[:-1]-=d
        return out
    diagonal=np.zeros(mask.shape)
    diagonal[:,:,1:]+=gx;diagonal[:,:,:-1]+=gx;diagonal[:,1:,:]+=gy;diagonal[:,:-1,:]+=gy
    diagonal[1:]+=gz;diagonal[:-1]+=gz;diagonal[fixed| (diagonal==0)]=1
    rhs=-laplace(boundary);rhs[fixed]=0
    solution=np.zeros(mask.shape);residual=rhs.copy();z=residual/diagonal;direction=z.copy();rz=float(np.sum(residual*z))
    startnorm=float(np.linalg.norm(rhs));rel=1.;started=time.monotonic()
    for iteration in ([] if '--amg' in sys.argv else range(1,6001)):
        applied=laplace(direction);applied[fixed]=direction[fixed]
        denom=float(np.sum(direction*applied))
        if denom<=0:raise RuntimeError('Non-positive CG denominator')
        alpha=rz/denom;solution+=alpha*direction;residual-=alpha*applied
        rel=float(np.linalg.norm(residual))/startnorm
        if rel<1e-9:break
        z=residual/diagonal;newrz=float(np.sum(residual*z));direction=z+(newrz/rz)*direction;rz=newrz
        if iteration%500==0:print('Mesh',step,'plating um',plating*1e6,'iteration',iteration,'relative residual',rel,flush=True)
    if '--amg' in sys.argv:
        from copper_amg import solve
        solution,iteration,rel=solve(gx,gy,gz,diagonal,fixed,rhs)
    assert rel<1e-7,'Unconverged resistance screen'
    voltage=solution+boundary;flux=laplace(voltage)
    source=float(flux[0,terminals['J1']].sum());sink=float(flux[0,terminals['J12']].sum())
    assert source>0 and abs(source+sink)/source<1e-5,'Current conservation failed'
    resistance=1/source
    reports.append({'plating_um_assumed':plating*1e6,'resistance_ohm_at_100C':resistance,
                    'drop_V_at_80A':80*resistance,'copper_and_via_loss_W_at_80A':6400*resistance,
                    'iterations':iteration,'relative_residual':rel,'current_balance_relative':abs(source+sink)/source})
    print(json.dumps(reports[-1]),flush=True)
report={'board_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'mesh_mm':step,
        'copper_um_all_layers_assumed':copper_um,
        'solver':'AMG-preconditioned CG' if '--amg' in sys.argv else 'Jacobi-preconditioned CG',
        'scope':'PGND DC resistance screening only, ideal equipotential solder-land contacts; not a thermal rating',
        'limitations':[f'Copper assumed uniformly 100 C and {copper_um:g} um on all four layers','Plating is assumed, not measured or fabricator accepted',
          'Copper thickness sweep keeps via segment lengths and XY geometry unchanged; no fabrication stackup is implied',
          'Via disks do not subtract drill bores; barrel connection is lumped at one raster node',
          'Rasterized pads omit rounded corners; vias use lumped barrel conductance','Mesh convergence must be checked',
          'No harness, connector, solder-joint or solder-void resistance','No prediction of temperature rise'],
        'results':reports}
prefix='ground_resistance_' if copper_um==70 else f'heavy_ground_{copper_um:g}um_'
(root/(prefix+str(step)+('_amg' if '--amg' in sys.argv else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n')
