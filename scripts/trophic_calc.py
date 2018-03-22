#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 14:32:09 2017

@author: robertmarsland
"""

import argparse
from community_simulator.cavity_threelevel import RunCommunity
import numpy as np
import distutils.dir_util
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("task_ID", type=int)
parser.add_argument("param", type=str)
parser.add_argument("scale", type=float)
parser.add_argument("ns", type=int)
args = parser.parse_args()

#folder = 'test'
folder = '/project/biophys/trophic_structure/dataJan18/vary_'+args.param
distutils.dir_util.mkpath(folder)
namelist = ['data','finalstate','simparams','cmatrix']
filenamelist = [folder+'/'+namelist[q]+'_'+str(args.task_ID)+'_K_eta'+'.xlsx' 
                for q in range(len(namelist))]
ic = [0,[0,1,2],0,[0,1]]
h = [0,0,[0,1],[0,1]]

n_iter = 1000
trials = 27
T=5
cutoff = 1e-6
S = 40

params = {'K':1.,
          'sigK':0.1,
          'muc':3,
          'sigc':1,
          'mud':3,
          'sigd':1,
          'm':0.5,
          'sigm':0.05,
          'u':0.5,
          'sigu':0.05,
          'gamma':1.,
          'eta':1.}

params[args.param] = args.scale*args.task_ID

Kvec = np.linspace(0.1,1,args.ns)
etavec = S*1./np.arange(20,80,int(round(60./args.ns)))
for j in range(len(Kvec)):
    print('K='+str(Kvec[j]))
    for m in range(len(etavec)):
        params['K']=Kvec[j]
        params['eta']=etavec[m]
            
        out = RunCommunity(params,S,trials=trials,run_number=j*len(etavec)+m,
                           n_iter=n_iter,T=T,cutoff=cutoff)
    
        if j==0 and m==0:
            for q in range(4):
                out[q].to_excel(filenamelist[q])
        else:
            for q in range(4):
                pd.read_excel(filenamelist[q],index_col=ic[q],header=h[q]).append(out[q]).to_excel(filenamelist[q])

        del out