# author
# date 2020.11.02
# python 3.8.6
import numpy as np
import matplotlib.pylab as plt


class FIRfilter:

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
        data = np.random.randint(0,10,20)
        h = np.array([1,2,3,2,1])
        h1 = FIRfilter(h)
        y = []
        for k in data:
           yn = h1.dofilter(k)
           y = np.append(y,yn)
        plt.plot(y)
if __name__ == "__main__":
        unittest()
