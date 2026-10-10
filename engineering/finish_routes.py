"""Rebuild the 2026-09-07 routing repair from its preserved input snapshot.

Requires --rebuild-from-backup. Run DRC and center_via_tracks.py afterwards.
This is a bounded repair script, not a general-purpose or ampacity-aware router.
"""
import sys
if '--rebuild-from-backup' not in sys.argv:
    raise SystemExit('Use --rebuild-from-backup explicitly; this replaces current board edits.')
import pcbnew as p
import heapq,math,json,time
from pathlib import Path
from sexpr import parse, dump, one
raw=parse(Path('engineering/before_resume_2145.kicad_pcb').read_text(encoding='utf-8'))
bad={'50a49f0c-9276-4a90-96fa-c300c15c09d8','7ba60dc7-549a-4988-857a-1713f8987047','ec10fe5a-f364-4838-8e1c-e4688a4f6881'}
bad.add('51f4e116-9d6b-48a3-8147-eb6aa10c738b')
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='segment' and one(v,'uuid')[1] in bad)]
Path('engineering/repair_input.kicad_pcb').write_text(dump(raw)+'\n',encoding='utf-8')
b=p.LoadBoard('engineering/repair_input.kicad_pcb')
import numpy as np
backup=Path('engineering/before_finish.kicad_pcb')
if not backup.exists():backup.write_bytes(Path('Swayatt_PCB.kicad_pcb').read_bytes())
fs={f.GetReference():f for f in b.GetFootprints()}
fs['TP1'].SetPosition(p.VECTOR2I(p.FromMM(81.85),p.FromMM(228)))
oldpads=[q.GetPosition() for q in fs['C16'].Pads()]
fs['C16'].SetPosition(fs['C16'].GetPosition()+p.VECTOR2I(p.FromMM(.3),0))
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):continue
    for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
        if any(getter()==pt for pt in oldpads):setter(getter()+p.VECTOR2I(p.FromMM(.3),0))
layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
step=.05;N=801;xx=60+np.arange(N)*step;yy=190+np.arange(N)*step
def rect(mask,x1,y1,x2,y2):
    i1=max(0,int(math.ceil((x1-60)/step)));i2=min(N,int(math.floor((x2-60)/step))+1)
    j1=max(0,int(math.ceil((y1-190)/step)));j2=min(N,int(math.floor((y2-190)/step))+1)
    mask[j1:j2,i1:i2]=True
def segment(mask,ax,ay,bx,by,r):
    i1=max(0,int(math.floor((min(ax,bx)-r-60)/step)));i2=min(N,int(math.ceil((max(ax,bx)+r-60)/step))+1)
    j1=max(0,int(math.floor((min(ay,by)-r-190)/step)));j2=min(N,int(math.ceil((max(ay,by)+r-190)/step))+1)
    if i1>=i2 or j1>=j2:return
    X=xx[i1:i2][None,:];Y=yy[j1:j2][:,None];dx=bx-ax;dy=by-ay;d=dx*dx+dy*dy
    u=np.clip(((X-ax)*dx+(Y-ay)*dy)/d,0,1) if d else 0
    mask[j1:j2,i1:i2] |= (X-ax-u*dx)**2+(Y-ay-u*dy)**2 <= r*r
def masks(net):
    blocked=np.zeros((4,N,N),dtype=bool);vb=np.zeros((N,N),dtype=bool)
    blocked[:,:13,:]=True;blocked[:,-13:,:]=True;blocked[:,:,:13]=True;blocked[:,:,-13:]=True
    vb[:16,:]=True;vb[-16:,:]=True;vb[:,:16]=True;vb[:,-16:]=True
    for f in fs.values():
        clearance=.1499 if f.GetReference() in ('U1','U3') else .1999
        for q in f.Pads():
            if q.GetNetname()==net:continue
            if not any(q.GetLayerSet().Contains(l) for l in layers):continue
            bb=q.GetBoundingBox();x1,y1,x2,y2=[p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())]
            r=clearance+.1
            for li,layer in enumerate(layers):
                if q.GetLayerSet().Contains(layer):rect(blocked[li],x1-r,y1-r,x2+r,y2+r)
            r=clearance+.25;rect(vb,x1-r,y1-r,x2+r,y2+r)
    for t in b.GetTracks():
        a,c=t.GetStart(),t.GetEnd();ax,ay,bx,by=[p.ToMM(v) for v in (a.x,a.y,c.x,c.y)]
        isvia=isinstance(t,p.PCB_VIA)
        width=p.ToMM(t.GetWidth(p.F_Cu) if isvia else t.GetWidth())
        if t.GetNetname()!=net:
            for li,layer in enumerate(layers):
                if isvia or t.GetLayer()==layer:segment(blocked[li],ax,ay,bx,by,width/2+.2999)
            segment(vb,ax,ay,bx,by,width/2+.455)
        elif isvia:
            # Avoid co-located or inadequately spaced drill holes.
            segment(vb,ax,ay,bx,by,(p.ToMM(t.GetDrillValue())+.2)/2+.255)
    return blocked,vb
def idx(x,y,layer):return (layer,int(round((y-190)/step)),int(round((x-60)/step)))
def route(net,start,end):
    blocked,vb=masks(net);s=idx(*start);goal=idx(*end)
    ownvias={idx(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y),0)[1:] for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==net}
    if net in ('/FB','/RT'):
        x,y=83.3,start[1]
        print('Via check',net,x,y, bool(vb[idx(x,y,0)[1:]]),flush=True)
        for t in b.GetTracks():
            if t.GetNetname()==net:continue
            a,c=t.GetStart(),t.GetEnd();ax,ay,bx,by=[p.ToMM(v) for v in (a.x,a.y,c.x,c.y)]
            dx,dy=bx-ax,by-ay;dd=dx*dx+dy*dy;u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/dd)) if dd else 0
            width=p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth())
            if math.hypot(x-ax-u*dx,y-ay-u*dy)<width/2+.455:print('track blocker',t.m_Uuid.AsString(),t.GetNetname(),b.GetLayerName(t.GetLayer()),ax,ay,bx,by,width,flush=True)
        for f in fs.values():
            for q in f.Pads():
                if q.GetNetname()==net or not any(q.GetLayerSet().Contains(l) for l in layers):continue
                bb=q.GetBoundingBox();r=(.1499 if f.GetReference() in ('U1','U3') else .1999)+.25
                if p.ToMM(bb.GetX())-r<=x<=p.ToMM(bb.GetRight())+r and p.ToMM(bb.GetY())-r<=y<=p.ToMM(bb.GetBottom())+r: print('via blocker',f.GetReference(),q.GetNumber(),q.GetNetname(),flush=True)
    if blocked[s] or blocked[goal]:
        print('Endpoint blocked',net,s,goal,blocked[s],blocked[goal],flush=True);return False
    def heuristic(v):return math.hypot(v[1]-goal[1],v[2]-goal[2])+(25 if v[0]!=goal[0] else 0)
    queue=[(heuristic(s),0,s)];cost={s:0};parent={};count=0;then=time.monotonic()
    while queue:
        _,g,u=heapq.heappop(queue)
        if g!=cost.get(u):continue
        if u==goal:break
        count+=1
        if count%100000==0:print(net,'search',count,'states',round(time.monotonic()-then,1),'s',flush=True)
        l,j,i=u
        candidates=[]
        for dj,di in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)):
            jj,ii=j+dj,i+di
            if not(0<=ii<N and 0<=jj<N) or blocked[l,jj,ii]:continue
            if dj and di and (blocked[l,j,ii] or blocked[l,jj,i]):continue
            candidates.append(((l,jj,ii),1.414214 if dj and di else 1.))
        if not vb[j,i] or (j,i) in ownvias:
            candidates.extend(((ll,j,i),25.) for ll in range(4) if ll!=l and not blocked[ll,j,i])
        for v,w in candidates:
            ng=g+w
            if ng<cost.get(v,float('inf')):
                cost[v]=ng;parent[v]=u;heapq.heappush(queue,(ng+heuristic(v),ng,v))
    else:
        print('No route',net,count,flush=True);return False
    path=[goal]
    while path[-1]!=s:path.append(parent[path[-1]])
    path.reverse();nobj=next(q.GetNet() for f in fs.values() for q in f.Pads() if q.GetNetname()==net)
    def line(a,c,layer):
        if math.dist(a,c)<1e-7:return
        t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(c[0]),p.FromMM(c[1])))
        t.SetLayer(layers[layer]);t.SetWidth(p.FromMM(.2));t.SetNet(nobj);b.Add(t)
    def point(node):return (float(xx[node[2]]),float(yy[node[1]]))
    line(start[:2],point(s),s[0]);line(point(goal),end[:2],goal[0])
    # Collapse collinear grid steps into normal KiCad track segments.
    anchor=path[0];last=anchor;direction=None
    for cur in path[1:]:
        if cur[0]!=last[0]:
            line(point(anchor),point(last),last[0]);x,y=point(cur)
            if cur[1:] not in ownvias:
                v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));v.SetWidth(p.FromMM(.5));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nobj);b.Add(v)
            anchor=cur;direction=None
        else:
            nd=(cur[1]-last[1],cur[2]-last[2])
            if direction is not None and nd!=direction:line(point(anchor),point(last),last[0]);anchor=last
            direction=nd
        last=cur
    line(point(anchor),point(last),last[0])
    print('Routed',net,'length/cost',round(cost[goal]*step,2),'mm',flush=True)
    return True
for pin,x,y in [('6',83.4,210.285),('7',83.145,209.63),('8',83.4,208.975)]:
    q=next(q for q in fs['U1'].Pads() if q.GetNumber()==pin)
    pos=p.VECTOR2I(p.FromMM(x),p.FromMM(y))
    v=p.PCB_VIA(b);v.SetPosition(pos);v.SetWidth(p.FromMM(.5));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(q.GetNet());b.Add(v)
    t=p.PCB_TRACK(b);t.SetStart(q.GetPosition());t.SetEnd(pos);t.SetWidth(p.FromMM(.2));t.SetLayer(p.B_Cu);t.SetNet(q.GetNet());b.Add(t)
jobs=[('/RT',(83.4,208.975,1),(93.,197.175,3)),
      ('/COMP',(83.4,210.285,1),(83.,205.775,3)),
      ('/FB',(83.145,209.63,1),(83.,204.225,3)),
      ('/FB',(83.145,209.63,1),(93.,204.175,3)),
      ('/out',(81.4143,211.6116,2),(85.5408,207.4851,2)),
      ('/PGND',(74.,228.9375,0),(76.,225.5,3))]
for f in fs.values():
    for q in f.Pads():
        bb=q.GetBoundingBox()
        if bb.GetX()<p.FromMM(84) and bb.GetRight()>p.FromMM(80) and bb.GetY()<p.FromMM(212) and bb.GetBottom()>p.FromMM(207):
            print(f.GetReference(),q.GetNumber(),q.GetNetname(),b.GetLayerName(q.GetLayer()),[p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())],flush=True)
success=[route(*job) for job in jobs]
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
print('Results',success,flush=True)
