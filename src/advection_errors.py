###################################################################################
#
# Module to compute the error convergence in L_inf, L1 and L2 norms
# for the advection equation using the Piecewise Parabolic Method (PPM)
# Luan da Fonseca Santos - April 2022
#
####################################################################################

from advection_2d import adv_2d
import numpy as np
from errors import *
from parameters_2d import simulation_adv_par_2d, graphdir
from advection_ic  import velocity_adv_2d

def error_analysis_adv2d(simulation):
    # Initial condition
    ic = simulation.ic

    # Velocity
    vf = simulation.vf

    # Reconstruction method
    recon = simulation.recon

    # Departure point method
    dp = simulation.dp

    # Operator splitting
    opsplit = simulation.opsplit

    # Test case
    tc = simulation.tc

    # CFL number for all simulations

    # Interval
    x0 = simulation.x0
    xf = simulation.xf
    y0 = simulation.y0
    yf = simulation.yf

    # Number of tests
    Ntest = 8

    # Number of cells
    N = np.zeros(Ntest)
    N[0] = 10
    M = np.zeros(Ntest)
    M[0] = 10

    # Timesteps
    dt = np.zeros(Ntest)

    u, v = velocity_adv_2d(x0, y0, 0, simulation)

    # Period
    if simulation.vf==1: # constant velocity
        Tf = 5.0
        dt[0] = 0.25
    elif simulation.vf == 2: # variable velocity
        Tf = 5.0
        dt[0] = 0.05
    elif simulation.vf == 3: # variable velocity
        Tf = 5.0
        dt[0] = 0.10
    else:
        exit()

    # Errors array
    #recons = (1,4)
    #deps = (1,2)
    #split = (1,3)

    recons = (simulation.recon,)
    deps = (simulation.dp,)
    split = (simulation.opsplit,)

    recon_names = ['PPM', 'mono_CW84','PPM_hybrid','mono_L04']
    dp_names = ['Euler', 'RK3']
    sp_names = ['L96', 'L04', 'PL07']
    error_linf = np.zeros((Ntest, len(recons), len(split), len(deps)))
    error_l1   = np.zeros((Ntest, len(recons), len(split), len(deps)))
    error_l2   = np.zeros((Ntest, len(recons), len(split), len(deps)))

    # Compute number of cells and time step for each simulation
    for i in range(1, Ntest):
        N[i]  = N[i-1]*2.0
        M[i]  = M[i-1]*2.0
        dt[i] = dt[i-1]*0.5

    # Let us test and compute the error
    d = 0
    for dp in deps:
        sp = 0
        for opsplit in split:
            rec = 0
            for recon in recons:
                for i in range(0, Ntest):
                    # Update simulation parameters
                    simulation = simulation_adv_par_2d(int(N[i]), int(M[i]), dt[i], Tf, ic, vf, tc, recon, dp, opsplit)

                    # Run advection routine and get the errors
                    error_linf[i,rec,sp,d], error_l1[i,rec,sp,d], error_l2[i,rec,sp,d] =  adv_2d(simulation, False)
                    print('\nParameters: N = '+str(int(N[i]))+', dt = '+str(dt[i]),', recon = ', recon,', split = ',opsplit, ', dp = ', dp)

                    # Output
                    print_errors_simul(error_linf[:,rec,sp,d], error_l1[:,rec,sp,d], error_l2[:,rec,sp,d], i)
                rec = rec+1
            sp = sp+1
        d = d+1

    # plot errors for different all schemes in  different norms
    error_list = [error_linf, error_l1, error_l2]
    norm_list  = ['linf','l1','l2']
    norm_title  = [r'$L_{\infty}$',r'$L_1$',r'$L_2$']

    e = 0
    for error in error_list:
        errors = []
        dep_name = []
        for d in range(0, len(deps)):
            for sp in range(0, len(split)):
                for r in range(0, len(recons)):
                    errors.append(error[:,r,sp,d])
                    dep_name.append(dp_names[deps[d]-1]+'-'+sp_names[sp-1]+'-'+recon_names[recons[r]-1])

        title = simulation.title + ' - ' + simulation.icname+', velocity = '+ str(simulation.vf)+', norm = '+norm_title[e]
        filename = graphdir+'2d_adv_tc'+str(tc)+'_ic'+str(ic)+'_vf'+str(vf)\
        +'_norm'+norm_list[e]+'_parabola_errors.pdf'
        plot_errors_loglog(N, errors, dep_name, filename, title)

        # Plot the convergence rate
        title = 'Convergence rate - ' + simulation.icname +', velocity = ' + str(simulation.vf)+', norm = '+norm_title[e]
        filename = graphdir+'2d_adv_tc'+str(tc)+'_ic'+str(ic)+'_vf'+str(vf)\
        +'_norm'+norm_list[e]+'_convergence_rate.pdf'
        plot_convergence_rate(N, errors, dep_name, filename, title)
        e = e+1
