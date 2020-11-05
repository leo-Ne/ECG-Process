import numpy as np
from scipy.fft import * 
import matplotlib.pyplot as plt
from cal_filter_para import *

def paint():
    src = np.load('einthoven_II.npy')
    sig1 = np.load('signal1.npy')
    sig2 = np.load('signal2.npy')
    plt.figure(figsize=(12, 6))
#    plt.plot(src, label='src')
    plt.plot(sig1, label='sig1')
    plt.plot(sig2, label='sig2')
    plt.legend()
    plt.savefig('result.png', bbox_inches='tight')
    pass

def analysis():
    w = np.arange(0, 250,250/30000)
    src = np.load('einthoven_II.npy')
    sig1 = np.load('signal1.npy')
    sig2 = np.load('signal2.npy')
    
    ft = np.abs(fft(src))
    ft1 = np.abs(fft(sig1))
    plt.figure(figsize=(12, 6))
    plt.plot(w, ft)
    plt.savefig('ft_src.png', bbox_inches='tight')

    plt.figure(figsize=(12, 6))
    plt.plot(w, ft1)
    plt.savefig('ft1.png', bbox_inches='tight')
    pass

def analysisFilter():
    M, Wc = 100, np.pi / 25
    n = np.arange(0, 250, 1)
#    hp = HP(194, np.pi/25)
    hp = np.sinc(np.pi * (n - M/2)) - (Wc / np.pi) * np.sinc(Wc * (n - M/2))
    lp = (Wc / np.pi) * np.sinc(Wc * (n - M/2))
    hp = np.sinc(np.pi * (n - M/2)) - lp
    hp = -lp
    hamming = Hamming(100)
#    hp = hp * hamming
    H = fft(hp)
    amp = np.abs(H)
#    pha = np.arctan(np.imag(H) / np.real(H))
#    amp = 10 * np.log10(amp)
    plt.figure(figsize=(12,6))
    plt.plot(amp)
    plt.savefig('hammingHP.png', bbox_inches='tight')
    pass
    

if __name__ == "__main__":
    paint()
#    analysisFilter()
    pass
