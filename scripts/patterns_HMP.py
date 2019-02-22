#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 17:23:10 2017

@author: robertmarsland
"""
import pandas as pd
import numpy as np
from community_simulator.usertools import MakeConsumerDynamics,MakeResourceDynamics,MakeMatrices,MakeInitialState,AddLabels
from community_simulator import Community
import pickle

n_samples = 300

#General Parameters
mp = {'sampling':'Binary', #Sampling method
    'SA': 5000, #Number of species in each family
    'MA': 300, #Number of resources of each type
    'Sgen': 0, #Number of generalist species
    'muc': 10, #Mean sum of consumption rates in Gaussian model
    'q': 0, #Preference strength (0 for generalist and 1 for specialist)
    'c0':0, #Background consumption rate in binary model
    'c1':1., #Specific consumption rate in binary model
    'fs':0.45, #Fraction of secretion flux with same resource type
    'fw':0.45, #Fraction of secretion flux to 'waste' resource
    'D_diversity':0.3, #Variability in secretion fluxes among resources (must be less than 1)
    'regulation':'independent',
    'replenishment':'external',
    'response':'type I'
    }

#Construct dynamics
def dNdt(N,R,params):
    return MakeConsumerDynamics(mp)(N,R,params)
def dRdt(N,R,params):
    return MakeResourceDynamics(mp)(N,R,params)
dynamics = [dNdt,dRdt]

#Construct matrices
c,D = MakeMatrices(mp)

#Set up the experiment
HMP_protocol = {'R0_food':1000, #unperturbed fixed point for supplied food
                'n_wells':3*n_samples, #Number of independent wells
                'S':4500, #Number of species per well
                'food':np.asarray(np.hstack((np.zeros(n_samples),1*np.ones(n_samples),
                                             2*np.ones(n_samples))),dtype=int) #index of food source
                }
HMP_protocol.update(mp)
#Make initial state
N0,R0 = AddLabels(*MakeInitialState(HMP_protocol),c)
init_state=[N0,R0]
metadata = pd.DataFrame(['Env. 1']*n_samples+['Env. 2']*n_samples+['Env. 3']*n_samples,
                        index=N0.T.index,columns=['Food Source'])
#Make parameter list
m = 1+0.01*np.random.randn(len(c))
params=[{'w':1,
        'g':1,
        'l':0.8,
        'R0':R0.values[:,k],
        'r':1.,
        'tau':1
        } for k in range(len(N0.T))]
for k in range(len(params)):
    params[k]['c'] = c
    params[k]['D'] = D
    params[k]['m'] = m


for S in [4500,2500,500]:
    HMP_protocol['S'] = S
    N0,R0 = AddLabels(*MakeInitialState(HMP_protocol),c)
    init_state=[N0,R0]
    HMP = Community(init_state,dynamics,params)
    HMP.SteadyState(verbose=True,plot=False,tol=1e-3)
    with open('/project/biophys/microbial_crm/data/HMP_S'+str(S)+'.dat','wb') as f:
        pickle.dump([HMP.N,HMP.R,params[0],R0,metadata],f)