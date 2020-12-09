# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 01:59:14 2020
"""


import numpy as np
import matplotlib.pylab as plt
import fir_filter


class Pre_proccess:
    def __init__(self):
        data = np.loadtxt('ECG_msc_matric_2.dat')
        plt.figure(1)
        time = np.linspace(0,20,len(data))
        plt.plot(time,data) #original plot
        self.data = data
        self.time = time

        self.fs = 250 #sample rate
        self.M = 200 #taps
        self.DC = 5 #DC parameter

    def run(self):
        M = self.M
        data = self.data.copy()
        fs = self.fs
        k1 = int(45/fs*M) # 50HZ filter out
        k2 = int(55/fs*M)
        k3 = int(5/fs*M)#  DC filter out

        X = np.ones(M)

        #filter out
        X[k1:k2+1] = 0
        X[M-k2:M-k1+1] = 0
        X[0:k3+1] = 0
        X[M-k3:M+1] = 0

        x = np.fft.ifft(X)
        x = np.real(x)

        h = np.zeros(M)

        h[0:int(M/2)] = x[int(M/2):M]

        h[int(M/2):M] = x[0:int(M/2)]

        h = h*np.hamming(M)
        n = fir_filter.FIRfilter(h)
        y = []
        for k in data:
            yn = n.dofilter(k)
            y = np.append(y,yn)
        plt.figure(2)
        plt.plot(y)


        # make a template after pre filtering : DC removal and 50Hz removal
        template = y[700:1000]
        plt.figure(3)
        plt.plot(template)
        #create fir coefficients by time reversing the template
        fir_coeff = template[::-1]
        plt.figure(4)
        plt.plot(fir_coeff)

        det = fir_filter.FIRfilter(fir_coeff)
        z = []
        for s in data:
            zn = n.dofilter(s)
            z = np.append(z,zn)
        plt.figure(5)
        plt.plot(z)

        z = z*z  #improve S/N
        plt.figure(6)
        plt.plot(z)
        return y


if __name__ == "__main__":
    session = Pre_proccess()
    session.run()
    print("Done! Success.")
    pass



