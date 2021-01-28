# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 05:27:58 2020

@author: a
"""

from ecg_gudb_database import GUDb
import matplotlib.pyplot as plt
import numpy as np
import fir_filter
#print experiments
subject_number = 12
experiments = 'walking'
ecg_class = GUDb(12,r'walking')# creating class which loads the experiment
einthoven_ii = ecg_class.einthoven_II

#plt.figure(1)
#plt.plot(einthoven_ii)

#plt.plot(template)

M = 200
fs = 250
DC = 5
k1 = int(45/fs*M) # 50HZ filter out 
k2 = int(55/fs*M)
k3 = int(5/fs*M)#  DC filter out
h = np.zeros(M)
X = np.ones(M)
X[k1:k2+1] = 0
X[M-k2:M-k1+1] = 0
X[0:k3+1] = 0
X[M-k3:M+1] = 0
x = np.fft.ifft(X)
x = np.real(x)
h[0:int(M/2)] = x[int(M/2):M]

h[int(M/2):M] = x[0:int(M/2)]
h = h*np.hamming(M)
n = fir_filter.FIRfilter(h)
y = []
for k in einthoven_ii:
    yn = n.dofilter(k)
    y = np.append(y,yn)
template = y[11778:11885]
plt.figure(3)
plt.plot(template)
fir_coeff = template[::-1] 

det = fir_filter.FIRfilter(fir_coeff)
z = []
for s in einthoven_ii:
    zn = n.dofilter(s)
    z = np.append(z,zn)
z = z*z  #improve S/N
plt.figure(6)
plt.plot(z)


''' Li is a stupid boy!!'''

