"""Analytical network checks independent of the PCB rasterizer."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
import numpy as np
from copper_amg import solve


def check(name, shape, edges, source, sink, expected):
    gx = np.zeros((shape[0], shape[1], shape[2]-1))
    gy = np.zeros((shape[0], shape[1]-1, shape[2]))
    gz = np.zeros((shape[0]-1, shape[1], shape[2]))
    for axis, index, conductance in edges:
        (gz, gy, gx)[axis][index] = conductance
    def laplace(v):
        out = np.zeros(shape)
        for g, a, b in ((gx, (slice(None),slice(None),slice(None,-1)), (slice(None),slice(None),slice(1,None))),
                        (gy, (slice(None),slice(None,-1),slice(None)), (slice(None),slice(1,None),slice(None))),
                        (gz, (slice(None,-1),slice(None),slice(None)), (slice(1,None),slice(None),slice(None)))):
            flow = g * (v[a]-v[b])
            out[a] += flow
            out[b] -= flow
        return out
    diagonal = np.zeros(shape)
    diagonal[:,:,:-1] += gx; diagonal[:,:,1:] += gx
    diagonal[:,:-1,:] += gy; diagonal[:,1:,:] += gy
    diagonal[:-1] += gz; diagonal[1:] += gz
    fixed = np.zeros(shape, bool)
    fixed[source] = True; fixed[sink] = True
    boundary = np.zeros(shape); boundary[source] = 1
    rhs = -laplace(boundary); rhs[fixed] = 0
    solution, iterations, residual = solve(gx, gy, gz, diagonal, fixed, rhs)
    voltage = solution + boundary
    flux = laplace(voltage)
    current = float(flux[source].sum())
    resistance = 1/current
    error = abs(resistance/expected-1)
    balance = abs(current+float(flux[sink].sum()))/current
    energy_error = abs(float(np.sum(voltage*flux))/current-1)
    assert error < 1e-8 and balance < 1e-8 and energy_error < 1e-8, name
    return dict(name=name, expected_ohm=expected, actual_ohm=resistance,
                relative_error=error, current_balance=balance,
                energy_balance=energy_error, solver_residual=residual)


cases = []
# Ten one-ohm series branches.
cases.append(check('series_strip', (1,1,11),
    [(2,(0,0,x),1.) for x in range(10)], (0,0,0), (0,0,10), 10.))
# Exceed max_coarse=100 to exercise multilevel preconditioning too.
cases.append(check('multilevel_series_strip', (1,1,202),
    [(2,(0,0,x),1.) for x in range(201)], (0,0,0), (0,0,201), 201.))
# Four identical strips in parallel, with lateral sheet conductance.
cases.append(check('rectangular_sheet', (1,4,11),
    [(2,(0,y,x),2.) for y in range(4) for x in range(10)] +
    [(1,(0,y,x),2.) for y in range(3) for x in range(11)],
    (0,slice(None),0), (0,slice(None),10), 10/(4*2)))
# Two plane segments and a vertical barrel in series: 2 + 3 + 5 ohms.
cases.append(check('via_and_planes', (2,1,2),
    [(2,(0,0,0),.5),(0,(0,0,1),1/3),(2,(1,0,0),.2)],
    (0,0,0), (1,0,0), 10.))
# An isolated conducting strip and isolated empty nodes must draw no current.
cases.append(check('floating_islands', (1,3,11),
    [(2,(0,y,x),1.) for y in (0,2) for x in range(10)],
    (0,0,0), (0,0,10), 10.))
report = {'scope':'Solver checks only; does not validate PCB geometry or ampacity',
          'passed':len(cases), 'cases':cases}
Path(__file__).with_name('copper_solver_tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
