####################################################################################
# This module contains the routine that computes one advection timestep
# Luan da Fonseca Santos - October 2022
####################################################################################

import numpy as np
from operator_splitting  import F_operator, G_operator
from advection_ic        import velocity_adv_2d, u_velocity_adv_2d, v_velocity_adv_2d
from flux                import compute_fluxes
from cfl                 import cfl_x, cfl_y

def adv_timestep(Q, u_edges, v_edges, F, G, FQ, GQ, px, py, cx, cy, Xu, Yu, Xv, Yv, t, simulation):

    N  = simulation.N    # Number of cells in x direction
    M  = simulation.M    # Number of cells in y direction

    # Ghost cells
    ngl = simulation.ngl
    ngr = simulation.ngr
    ng  = simulation.ng

    # Grid interior indexes
    i0 = simulation.i0
    iend = simulation.iend
    j0 = simulation.j0
    jend = simulation.jend

    # CFL calculation
    cx[:,:] = cfl_x(u_edges, simulation)
    cy[:,:] = cfl_y(v_edges, simulation)

    # Compute the fluxes
    compute_fluxes(Q, Q, px, py, cx, cy, simulation)

    # Applies F and G operators
    F_operator(FQ, u_edges, px.f_upw, cx, simulation)
    G_operator(GQ, v_edges, py.f_upw, cy, simulation)

    # Compute the fluxes again
    compute_fluxes(Q + 0.5*GQ, Q + 0.5*FQ, px, py, cx, cy, simulation)

    # Applies F and G operators again
    F_operator(F, u_edges, px.f_upw, cx, simulation)
    G_operator(G, v_edges, py.f_upw, cy, simulation)

    # Update
    Q[i0:iend,j0:jend] = Q[i0:iend,j0:jend] + F[i0:iend,j0:jend] + G[i0:iend,j0:jend]

    # Periodic boundary conditions
    # x direction
    Q[iend:N+ng,:] = Q[i0:i0+ngr,:]
    Q[0:i0,:]      = Q[N:N+ngl,:]

    # y direction
    Q[:,jend:N+ng] = Q[:,j0:j0+ngr]
    Q[:,0:j0]      = Q[:,M:M+ngl]

    # Updates for next time step
    if simulation.vf >= 2:
        # Velocity update
        u_edges[:,:] = u_velocity_adv_2d(Xu, Yu, t, simulation)
        v_edges[:,:] = v_velocity_adv_2d(Xv, Yv, t, simulation)


