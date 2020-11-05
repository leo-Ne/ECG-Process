import numpy as np
import matplotlib.pyplot as plt
from ecg_gudb_database import GUDb

def Hamming(M):
    n = np.arange(0, M+1, 1, dtype=np.float32)
    wn = 0.54 - 0.46 * np.cos(2 * np.pi * n / M)
    return wn

def LP(M:int, Wc:np.float32):
    n = np.arange(0, M+1, 1, dtype=np.float32)
    lp = (Wc / np.pi) * np.sinc(Wc * (n - M/2))
    lp_Wn = Hamming(M) * lp
    return lp_Wn

def HP(M:int, Wc:np.float32):
    n = np.arange(0, M+1, 1, dtype=np.float32)
    hp = np.sinc(np.pi * (n - M/2)) - (Wc / np.pi) * np.sinc(Wc * (n - M/2))
    hp_Wn = Hamming(M) * hp
    return hp_Wn

def MedianFilter(subseq:np.ndarray, v:np.float32):
    return v - np.median(subseq)

def convolution(x:np.ndarray, h:np.ndarray, M=None):
    if M is None:
        M = np.shape(h)[0]
    result = 0
    for i, elm in enumerate(x[x.size-M:]):
        result += elm * h[M-i-1]
    return result

def testUnit():
    h = Hamming(10)
    print(h)
    LP(10, np.pi / 2)
    HP(10, np.pi / 2)
    x = np.array([1, 4, 2, 3], np.float32)
    h = np.array([2, 4, 1], np.float32)
    val = convolution(x, h)
    pass

if __name__ == "__main__":
    testUnit()
