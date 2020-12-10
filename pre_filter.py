#! /use/bin/env python
''' **************************************
# Author       :leo-Ne
# Last modified:2020-12-10 20:07
# Email        : leo@email.com
# Filename     :cal_filter_para.py
# Description  : 
**************************************'''
import numpy as np

class SmothFilter:
    def __init__(self, _coefficients=None):
        """
        This class designed for n-order flat filter
        """
        if _coefficients is None:
            _coefficients = np.ones([1], np.float32)
        coefficients       = np.array(_coefficients, np.float32)
        self._coefficients = np.squeeze(coefficients)
        self._filterL      = np.size(coefficients)
        # M5_filter
        self._buf = np.zeros([self._filterL,], np.float32)
        self._cnt = 0
        pass

    def process(self, v):
        if v is None:
            sys.exit('Error:<None data input>')
            return None
        else:
            # filter update temporary store.
            self._buf[:-1] = self._buf[1:]
            self._buf[-1]  = v
            # filter output
            if self._cnt < self._filterL-1:
                self._cnt += 1
                result    = 0.0
            else:
                result   = np.dot(self._buf, self._coefficients.T)
        return result

def MedianFilter(subseq:np.ndarray, v:np.float32):
    return v - np.median(subseq)

def testUnit():
    print("It's kidding. This package is all right.")
    pass

if __name__ == "__main__":
    testUnit()
