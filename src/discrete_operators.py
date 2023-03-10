####################################################################################
# This module contains the routine that computes the discrete
# differential operator using finite volume discretization
# Luan da Fonseca Santos - 2023
####################################################################################

import numpy as np
from flux import compute_fluxes
import numexpr as ne

####################################################################################
# Given Q, compute div(UQ), where U = (u,v), and cx and cy
# are the cfl numbers (must be already computed)
# The divergence is given by px.dF + py.dF
####################################################################################
def divergence(Q, div, px, py, cx, cy, simulation):
    # Compute the fluxes
    compute_fluxes(Q, Q, px, py, cx, cy, simulation)

    # Applies F and G operators
    F_operator(px.dF, px.f_upw, cx, simulation)
    G_operator(py.dF, py.f_upw, cy, simulation)

    N = simulation.N
    ng = simulation.ng

    # Splitting scheme
    if simulation.opsplit==1:
        pxdF = px.dF
        pydF = py.dF
        Qx = ne.evaluate("Q+0.5*pxdF")
        Qy = ne.evaluate("Q+0.5*pydF")
    elif simulation.opsplit==2:
        # L04 equation 7 and 8
        #px.dF = px.dF + (cx[1:,:]-cx[:N+ng,:])*Q
        #py.dF = py.dF + (cy[:,1:]-cy[:,:N+ng])*Q
        #Qx = Q+0.5*px.dF
        #Qy = Q+0.5*py.dF
        pxdF = px.dF
        pydF = py.dF
        c1x, c2x = cx[1:,:], cx[:N+ng,:]
        c1y, c2y = cy[:,1:], cy[:,:N+ng]
        Qx = ne.evaluate('(Q + 0.5*(pxdF + (c1x-c2x)*Q))')
        Qy = ne.evaluate('(Q + 0.5*(pydF + (c1y-c2y)*Q))')
    elif simulation.opsplit==3:
        # PL07 - equation 17 and 18
        #Qx = 0.5*(Q + (Q + px.dF)/(1.0-(cx[1:,:]-cx[:N+ng,:])))
        #Qy = 0.5*(Q + (Q + py.dF)/(1.0-(cy[:,1:]-cy[:,:N+ng])))
        pxdF = px.dF
        pydF = py.dF
        c1x, c2x = cx[1:,:], cx[:N+ng,:]
        c1y, c2y = cy[:,1:], cy[:,:N+ng]
        Qx = ne.evaluate('0.5*(Q + (Q + pxdF)/(1.0-(c1x-c2x)))')
        Qy = ne.evaluate('0.5*(Q + (Q + pydF)/(1.0-(c1y-c2y)))')

    # Compute the fluxes again
    compute_fluxes(Qy, Qx, px, py, cx, cy, simulation)

    # Applies F and G operators again
    F_operator(px.dF, px.f_upw, cx, simulation)
    G_operator(py.dF, py.f_upw, cy, simulation)

    # Compute the divergence
    pxdF = px.dF
    pydF = py.dF
    dt = simulation.dt
    div[:,:] = ne.evaluate("-(pxdF + pydF)/dt")

####################################################################################
# Flux operator in x direction
# Inputs: Q (average values),
# u_edges (velocity in x direction at edges)
# Formula 2.7 from Lin and Rood 1996
####################################################################################
def F_operator(F, flux_x, cx, simulation):
    N = simulation.N
    i0 = simulation.i0
    iend = simulation.iend

    #F[i0:iend,:] = -(cx[i0+1:iend+1,:]*flux_x[i0+1:iend+1,:] - cx[i0:iend,:]*flux_x[i0:iend,:])
    c1 = cx[i0+1:iend+1,:]
    c2 = cx[i0:iend,:]
    f1 = flux_x[i0+1:iend+1,:]
    f2 = flux_x[i0:iend,:]
    F[i0:iend,:] = ne.evaluate("-(c1*f1-c2*f2)")
####################################################################################
# Flux operator in y direction
# Inputs: Q (average values),
# v_edges (velocity in y direction at edges)
# Formula 2.8 from Lin and Rood 1996
####################################################################################
def G_operator(G, flux_y, cy, simulation):
    M = simulation.M
    j0 = simulation.j0
    jend = simulation.jend

    #G[:,j0:jend] = -(cy[:,j0+1:jend+1]*flux_y[:,j0+1:jend+1] - cy[:,j0:jend]*flux_y[:,j0:jend])
    c1 = cy[:,j0+1:jend+1]
    c2 = cy[:,j0:jend]
    g1 = flux_y[:,j0+1:jend+1]
    g2 = flux_y[:,j0:jend]
    G[:,j0:jend] = ne.evaluate("-(c1*g1-c2*g2)")

