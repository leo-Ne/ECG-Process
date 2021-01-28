#! /use/bin/env python
''' **************************************
# Author       :leo-Ne
# Last modified:2020-12-10 15:53
# Email        : leo@email.com
# Filename     :heartrateDetection.py
# Description  : 
**************************************'''
import  numpy as np
from ecg_gudb_database import GUDb
from pre_filter import SmothFilter, MedianFilter
from matplotlib import pyplot as plt
from matplotlib import axes as axs

class heartRateDetection:
    """
    Detection without buffer is suitable for real time processing. 
    """
    def __init__(self, wt=20, fs=250):
        """
        Initialization
        """
        self._ecgSrc = None
        self._signal  = None
        # R peak annotations
        self._peakLoc    = None
        # ECG signal process setting
        self._fs        = fs
        self._wt        = wt
        # ECG peak detection setting
        self._threshold = 0
        # heartRate
        self._rate      = -1
        return 

    def loadData(self, filename=None):
        """
        Load the ECG data. File type is *.npy, 1-D ndarray.
        File einthoven_ii.npy store the ecg_class.einthoven_II data. 
        The reson I did this is my slow internet.
        """
        # ecg_class = GUDb(12, 'walking')
        # einthoven_ii = ecg_class.einthoven_II
        # self._fs     = ecg_class.fs
        if filename is None:
            data = np.load(r'einthoven_II.npy')
        else:
            data = np.load(filename)
        data = data[:-500]
        self._ecgSrc = data.copy()
        del data
        return

    def pre_process(self, R=34):
        ecg      = np.abs(self._ecgSrc)
        # Median filter cuts off DC. 
        signal1 = np.zeros([np.size(ecg),], np.float32)
        for i, v in enumerate(ecg):
            if i < R:
                subseq = ecg[:i+R]
            elif i > ecg.shape[0]-R:
                subseq = ecg[-i-R:-1]
            else:
                subseq = ecg[i-R:i+R]
            signal1[i] = MedianFilter(subseq, v)
        
        # Mean-5 filter cuts off 50Hz power line interference.
        M5       = np.ones([5, ], np.float32) / 5.0
        M5Filter = SmothFilter(M5)
        signal   = np.zeros_like(signal1)
        for i, v in enumerate(signal1):
            value     = M5Filter.process(v)
            signal[i] = value

        # Cut off the ecg less than 0
        threshold_value  = np.max(signal) / 2
        lowIndex         = np.where(signal < threshold_value)
        signal[lowIndex] = 0

        self._signal     = signal * 2
        self._threshold  = threshold_value
        del ecg, signal, signal1, lowIndex, subseq,M5, M5Filter, value, threshold_value
        return 

    def matched_v0(self):
        """
        Check R peak location index.
        """
        ecg = self._signal.copy()
        wt      = self._wt
        peak     = [-1]
        indx     = [-1]
        signal_W = np.zeros([wt], np.float32)
        i        = 0
        while i < ecg.shape[0]:
            # Slice ecg data
            if i + wt > ecg.shape[0]: # Save to the buffer.
                break
            else:
                signal_W[:] = ecg[i:i+wt]
                i += wt
            # detect the Peak.
            max_val = np.max(signal_W)
            index = np.argwhere(signal_W == max_val)
            if max_val == 0:            # signal_W is between peak and peak.
                if peak[-1] != -1:
                    peak.append(-1)
                    indx.append(-1)
#                else:
#                    continue
            else:                       #signal_W include peak envelope
                if max_val > peak[-1]:     ## cur_val > post_value
                    peak[-1] = max_val
                    indx[-1] = np.max(index + i - wt)
#                elif max_val <= peak[-1]:  ## cur_val <= post_value
#                    continue
        self._peakLoc = np.array(indx, np.float32)
        del ecg, wt, peak, indx, signal_W, i, max_val, index 
        return 

    def matched_v1(self):
        """
        This is very stupid code design!!!!!!!!!!!!!!!! 
        The data in computer is always digital.
        """
        
        ecg = self._ecgSrc.copy()
        threshold_value = self._threshold * 0.5
        ab_Loc = np.squeeze(np.where(ecg == threshold_value))
        ab_Len = np.size(ab_Loc)

        a_Loc  = np.zeros([np.int(ab_Len/2),], np.int)
        b_Loc  = np.zeros_like(a_Loc)
        index = np.arange(0, 2*np.size(a_Loc),step=2,dtype=np.int)
        
        # First zero and last zero
        print(np.shape(ab_Loc))
        first_p      = ab_Loc[0]
        last_p       = ab_Loc[-1]
        first_pValue = ecg[first_p+10]
        last_pValue  = ecg[last_p-10]
        # 4 condition.
        if first_pValue > 0 and last_pValue > 0:
            a_Loc = ab_Loc[index]
            b_Loc = ab_Loc[index+1]
        elif first_pValue > 0 and last_pValue < 0:
            a_Loc = ab_Loc[index]
            b_Loc = ab_Loc[index+1]
        elif first_pValue < 0 and last_pValue > 0:
            a_Loc = ab_Loc[index+1]
            b_Loc = ab_Loc[index+2]
        elif first_pValue < 0 and last_pValue < 0:
            a_Loc = ab_Loc[index[:-1]+1]
            b_Loc = ab_Loc[index[:-1]+2]

        length = b_Loc - a_Loc + 1
        envelope = np.zeros([np.size(a_Loc), np.max(length)])
        heartBeatsAnno = np.zeros_like(a_Loc)
        for i in range(np.size(a_Loc)):
            envelope[i, :length[i]] = ecg[a_Loc[i]:b_Loc[i]]
            heartBeatsAnno[i] = a_Loc + np.max(np.where(envelope[i] == np.max(envelope[i])))
        print("V1 match.")
        print(heartBeatsAnno.shape)

        return 

    def calculateHeatrate(self):
        fs        = self._fs
        intervals = np.diff(self._peakLoc)
        # rate: Sample point cost between two beats.
        rate      = np.sum(intervals) / intervals.shape[0]
        # count beats per minute.
        time       = self._peakLoc * (1.0 / fs)
        time       = np.squeeze(time)
        heart_rate = 60.0 / (intervals/float(fs))
        heart_rate = np.squeeze(heart_rate)
        # show result by heart rate digram
        plt.figure(figsize=(12, 6))
        plt.ylim(-1.0, 160.0)
        plt.xlabel('Times(s)')
        plt.ylabel('Heart rate / BPM')
        plt.plot(time[1:], heart_rate, linewidth=3, label='heart rate / BPM')
        plt.hlines(np.mean(heart_rate),time[1],time[-1],colors='#FF0000', label='Average heart rate')
        plt.savefig('heartRate.png', bbox_inches='tight')
        plt.show()
        # log rate 
        self._rate = rate / self._fs
        return 

def unittest():
    # test unit for Class heartRateDetection
    ECGFile = r'einthoven_II.npy'
    wt      = 20
    fs      = 250.0
    session = heartRateDetection(wt,fs)
    session.loadData(filename=ECGFile)
    session.pre_process()
    session.matched_v0()
#    session.matched_v1()
    session.calculateHeatrate()
    return 

if __name__ == "__main__":
    unittest()
