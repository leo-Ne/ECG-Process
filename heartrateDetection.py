#! /use/bin/env python
''' **************************************
# Author       :leo-Ne
# Last modified:2020-12-10 15:53
# Email        : leo@email.com
# Filename     :heartrateDetection.py
# Description  : 
**************************************'''
from ecg_gudb_database import GUDb
from cal_filter_para import Pre_filter
# from fir_filter_leone import unittest
import  numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as axs

class heartRateDetection:
    def __init__(self, wt=20, fs=250):
        """
        Initialization
        """
        self._ecgSrc = None
        self._signal  = None
        # Set a buffer to store data when size(data) less than wt
        self._buffer = None
        # R peak annotations
        self.anno    = None
        # ECG signal process setting
        self._fs     = fs
        self._wt     = wt
        # heartRate
        self.rate    = -1
        return 

    def loadData(self, subject_number=None, experiment=None):
        """
        Load the ECG data.
        File einthoven_ii.npy store the ecg_class.einthoven_II data. 
        The reson I did this is my slow internet.
        """
        # ecg_class = GUDb(12, 'walking')
        # print('fs:', ecg_class.fs)
        # einthoven_ii = ecg_class.einthoven_II
        # self._fs     = ecg_class.fs
        einthoven_ii = np.load(r'einthoven_II.npy')
        self._ecgSrc = einthoven_ii.copy()
        del einthoven_ii
        return

    def pre_process(self, R=34):
        M5      = np.ones([5, ], np.float32) / 5.0
        process = Pre_filter(M5)
        ecg     = np.abs(self._ecgSrc)
        
        # Median filter cuts off DC. 
        signal1 = np.zeros([ecg.shape[0],], np.float32)
        for i, v in enumerate(ecg):
            if i < R:
                subseq = ecg[:i+R]
            elif i > ecg.shape[0]-R:
                subseq = ecg[-i-R:-1]
            else:
                subseq = ecg[i-R:i+R]
            signal1[i] = process.MedianFilter(subseq, v)
        
        # Mean-5 filter cuts off 50Hz power line interference.
        signal2 = np.zeros([signal1.shape[0], ], np.float32)
        for i, v in enumerate(signal1):
            value = process.M5filter(v)
            signal2[i] = value

        # Cut off the ecg less than 0
        threshold_value   = np.max(signal2) / 2
        lowIndex          = np.where(signal2 < threshold_value)
        signal2[lowIndex] = 0
        self._signal      = signal2 * 2
        return signal2

    def matched(self, ecg=None):
        """
        Check R peak location index.
        """
        if ecg is None:
            ecg = self._signal.copy()
        wt       = self._wt

        peak     = [-1]
        indx     = [-1]
        signal_W = np.zeros([wt], np.float32)
        i        = 0
        while i < ecg.shape[0]:
            if i + wt > ecg.shape[0]: # Save to the buffer.
                self._buffer = ecg[i:].copy()
            else:
                if i == 0 and self._buffer is not None:
                    l = np.shape(self._buffer)[0]
                    signal_W[:l] = self._buffer[:]
                    signal_W[l:] = ecg[:wt-l]
                    i += wt-l
                else:
                    signal_W[:] = ecg[i:i+wt]
                    i += wt
                # find max value

                max_val = np.max(signal_W)
                index = np.argwhere(signal_W == max_val)
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
        plt.plot(self._ecgSrc)
        for line in indx:
            plt.vlines(line, -0.02, -0.016, colors='red')
#        plt.show()
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
#        plt.show()
        self.rate = rate / self._fs
        return self.rate


def unittest():
    # test unit for Class heartRateDetection
    session = heartRateDetection(wt=20)
    session.loadData()
    session.pre_process()
    session.matched()
    result = session.calculateHeatrate()
    print(result)
    pass


if __name__ == "__main__":
    unittest()
