# author leo
# date 2020.11.02
# python 3.8.6
import numpy as np
from ecg_gudb_database import GUDb
from cal_filter_para import *

class FIR_filter:

    def __init__(self, _coefficients):
        # my code here
        # filter coefficient
        coefficients      = np.array(_coefficients, np.float32)
        self.coefficients = np.squeeze(coefficients)
        self.filter_l     = np.shape(self.coefficients)[0]
        # buffer and count
        self.buf = np.zeros([self.filter_l,], np.float32)
        self.cnt = 0
        # buffer filtered signal
        pass 

    def dofilter(self, v):
        # my code here
        # buffer
        if v is None:
            print('Eeror data input!')
            return np.NaN
        elif v is not None:
            self.buf[:-1] = self.buf[1:]
            self.buf[-1]  = v
            if self.cnt < self.filter_l-1:
                self.cnt += 1
                result    = 0.0
            else:
                result    = np.sum(self.buf * self.coefficients, dtype=np.float32)
# more graceful style code, but this style has a bug which is not solved yet.
#            result        = np.matmul(self.buf, self.coefficients.T)
        return result


def unittest():
    # test unit for Class FIR_filter
    # load ecg data
    subject_number = 12
    experiment     = r'walking'
#    ecg_class      = GUDb(subject_number, experiment)
#    einthoven_ii   = ecg_class.einthoven_II
    einthoven_ii = np.load(r'einthoven_II.npy')
    einthoven_ii = np.abs(einthoven_ii)
    # filter coefficients
    "Important part, Calculate filter coefficients and write to the array!!!!"
    "I write an array of coefficients,  of which delay time is 4 point and amplitude reducing is half."
    filter_coeficients = np.array([1/5, 1/5, 1/5, 1/5, 1/5], np.float32)
    # buffer filtered ecg signal
    # using median to reduce DC
    signal1 = np.zeros([einthoven_ii.shape[0],], np.float32)
    R = 34
    for i, v in enumerate(einthoven_ii):
        if i < R:
            subseq = einthoven_ii[:i+R]
        elif i > einthoven_ii.shape[0]-R:
            subseq = einthoven_ii[-i-R:-1]
        else:
            subseq = einthoven_ii[i-R:i+R]
        signal1[i] = MedianFilter(subseq, v)
    np.save('signal1.npy', signal1)
    # test filter and process ecg signal
    signal2 = np.zeros([signal1.shape[0], ], np.float32)
    process = FIR_filter(filter_coeficients)
    for i, v in enumerate(signal1):
        value = process.dofilter(v)
        if value == np.NaN:
            print('Error data input!')
            break
        else:
            signal2[i] = value
    np.save('signal2.npy', signal2)

    print(signal1[200:])
    print(signal2[200:])
    pass

if __name__ == "__main__":
    unittest()
