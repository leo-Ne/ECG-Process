# author leo
# date 2020.11.02
# python 3.8.6
from ecg_gudb_database import GUDb
from cal_filter_para import Pre_filter
# from fir_filter_leone import unittest
import  numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as axs

class heartRateDetection:
    def __init__(self, _wt=None):
        # initialization
        self.ecg_src = None
        if _wt is None:
            _wt = 20
        self.wt = _wt
        self.signal = None
        # buffer for next
        self.buf = None
        # heartBeatsTimes
        self.anno = np.zeros([], np.float32)
        # heartRate
        self.fs   = 250
        self.rate = 0
        pass

    def loadECG(self, subject_number=None, experiment=None):
        # load ECG data
        # ecg_class = GUDb(12, 'walking')
        # print('fs:', ecg_class.fs)
        # einthoven_ii = ecg_class.einthoven_II
        einthoven_ii = np.load(r'einthoven_II.npy')
        self.ecg_src = einthoven_ii.copy()
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
                signal2[i] = value
        threshold_value = np.max(signal2) / 2
        for i, v in enumerate(signal2):
            if v < threshold_value:
                signal2[i] = 0
            else:
                signal2[i] *= 2
        self.signal = signal2.copy()
        return signal2

    def matched(self, ECG=None):
        wt = self.wt
        if ECG is None:
            ECG = self.signal.copy()
        i = 0
        peak = [-1]
        indx = [-1]
        Win = np.zeros([wt], np.float32)
        while i < ECG.shape[0]:
            if i + wt > ECG.shape[0]: # Save to the buffer.
                self.buf = ECG[i:].copy()
                pass
            else:
                if i == 0 and self.buf is not None:
                    l = np.shape(self.buf)[0]
                    Win[:l] = self.buf[:]
                    Win[l:] = ECG[:wt-l]
                    i += wt-l
                else:
                    Win[:] = ECG[i:i+wt]
                    i += wt
                # find max value

                max_val = np.max(Win)
                index = np.argwhere(Win == max_val)
                if max_val == 0:            # R-R
                    if peak[-1] != -1:
                        peak.append(-1)
                        indx.append(-1)
                    else:
                        continue
                else:
                    if max_val > peak[-1]:     # cur_val > post_value
                        peak[-1] = max_val
                        indx[-1] = index + i - wt
                    elif max_val <= peak[-1]:    # cur_val <= post_value
                        continue
        plt.figure(figsize=(12, 6))
        plt.plot(self.ecg_src)
        for line in indx:
            plt.vlines(line, -0.02, -0.016, colors='red')
        plt.show()
        self.anno = np.array(indx, np.float32)
        return indx

    def calculateHeatrate(self):
        # calculate the heatrate according to the ECG given
        fs = 250
        intervals = self.anno[1:] - self.anno[:-1]    # 等效于np.diff(self.index)
        rate = np.sum(intervals) / intervals.shape[0]
        heart_rate = 60.0 / (intervals/float(fs))
        time = self.anno * (1.0 / fs)
        time = np.squeeze(time)
        heart_rate = np.squeeze(heart_rate)
        plt.figure(figsize=(12, 6))
        plt.xlabel('Times(s)')
        plt.ylabel('Heart rate / BPM')
        plt.plot(time[1:], heart_rate)
        plt.savefig('heartRate.png', bbox_inches='tight')
        plt.show()
        self.rate = rate / self.fs
        return self.rate


def unittest():
    # test unit for Class heartRateDetection
    session = heartRateDetection(_wt=20)
    ecg = session.loadECG()
    session.pre_process(ecg)
    session.matched()
    result = session.calculateHeatrate()
    print(result)
    pass


if __name__ == "__main__":
    unittest()
