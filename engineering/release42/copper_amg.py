"""Sparse solution of the same grounded copper-network operator used by the screen."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
import pyamg

def solve(gx,gy,gz,diagonal,fixed,rhs):
    ids=np.full(fixed.shape,-1,np.int32);ids[~fixed]=np.arange(np.count_nonzero(~fixed),dtype=np.int32)
    row=[];col=[];data=[]
    for conductance,a,b in ((gx,ids[:,:,:-1],ids[:,:,1:]),(gy,ids[:,:-1,:],ids[:,1:,:]),(gz,ids[:-1],ids[1:])):
        select=(conductance>0)&(a>=0)&(b>=0)
        u=a[select];v=b[select];g=conductance[select]
        row.extend((u,v));col.extend((v,u));data.extend((-g,-g))
    n=np.count_nonzero(~fixed)
    off=sparse.coo_matrix((np.concatenate(data),(np.concatenate(row),np.concatenate(col))),shape=(n,n)).tocsr()
    diag=diagonal[~fixed]
    A=off+sparse.diags(diag,format='csr')
    # Floating raster islands have no excitation; omit them rather than adding
    # invented leakage conductance that could distort resistance results.
    count,labels=connected_components(off,directed=False)
    anchor=diag+np.asarray(off.sum(axis=1)).ravel()
    anchored=np.bincount(labels,weights=np.maximum(anchor,0),minlength=count)>1e-6
    keep=anchored[labels];A=A[keep][:,keep].tocsr();load=rhs[~fixed][keep]
    print('AMG copper nodes:',A.shape[0],'matrix entries:',A.nnz,'floating nodes omitted:',np.count_nonzero(~keep),flush=True)
    ml=pyamg.smoothed_aggregation_solver(A,symmetry='symmetric',max_coarse=100)
    history=[]
    x=ml.solve(load,tol=1e-11,maxiter=500,accel='cg',residuals=history)
    relative=float(np.linalg.norm(load-A@x)/np.linalg.norm(load))
    result=np.zeros(fixed.shape);free=np.zeros(n);free[keep]=x;result[~fixed]=free
    print('AMG iterations:',len(history)-1,'true relative residual:',relative,flush=True)
    return result,len(history)-1,relative
