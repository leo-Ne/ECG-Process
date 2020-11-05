# author leo
# date 2020.11.02
# python 3.8.6
from ecg_gudb_database import GUDb
from cal_filter_para import Pre_filter
import numpy as np
from matplotlib import pyplot as plt

class heartRateDetection:
    def __init__(self, _wt:int):
        # initialization 
        self.wt = _wt
        pass

    def loadECG(self, subject_number=None, experiment=None):
        # load ECG data
#        ecg_class = GUDb(subject_number, experiment)
#        einthoven_ii = ecg_class.einthoven_II
        einthoven_ii = np.load(r'einthoven_II.npy')
        return einthoven_ii

    def pre_process(self, ecg):
        M5 = np.array([1/5, 1/5, 1/5, 1/5, 1/5], np.float32)
        process = Pre_filter(M5)
        ecg = np.abs(ecg)
        signal1 = np.zeros([ecg.shape[0],], np.float32)
        R = 34
        for i, v in enumerate(ecg):
            if i < R:
                subseq = ecg[:i+R]
            elif i > ecg.shape[0]-R:
                subseq = ecg[-i-R:-1]
            else:
                subseq = ecg[i-R:i+R]
            signal1[i] = process.MedianFilter(subseq, v)           
        signal2 = np.zeros([signal1.shape[0], ], np.float32)
        for i, v in enumerate(signal1):
            value = process.M5filter(v)
            if value == np.NaN:
                print('Error data input!')
                break
            else:
                if value < 0:
                    value = 0
                signal2[i] = value
        threshold_value = np.max(signal2) / 2 
        plt.figure(figsize=(12, 6))
        plt.plot(signal2)
        print('threshold_value:', threshold_value)
        plt.savefig('threshold.png', bbox_inches='tight')

        pass

    def matched(self, ECG):
        # detect P peak
        pass

    def calculateHeatrate(self):
        # calculate the heatrate according to the ECG given
        pass

def unittest():
    # test unit for Class heartRateDetection
    session = heartRateDetection(_wt=1000)
    ecg = session.loadECG()
    session.pre_process(ecg)

    pass


if __name__ == "__main__":
    unittest()
