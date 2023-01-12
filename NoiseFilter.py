#!/usr/bin/env python3

"""
This class implements noise filtering. The concept is to compute 
time-averaged power spectra (before other filtering?) and multiply
each bin by (1.0 - avg/max). Subtracting an average bin value seems 
to introduce artifacts so, hopefully, this approach will be "quieter" 
and adapt automatically. 
"""
import numpy
import math as m

N_FFT = 1024
SAMPLE_FREQ = 44100 # typical sampling frequency
NYQUISTFREQ = SAMPLE_FREQ // 2  # Nyquist Frequency

def freqtobin(freq):
    return int((N_FFT - 1) * freq / NYQUISTFREQ + 0.5) + 1

LOWFREQ = freqtobin(30)  # lower limit for hearing range
UPPERFREQ = freqtobin(4500)  # upper limit for hearing range
MAXBIRDFREQ = freqtobin(12000)

class NoiseFilter(object):
    def __init__(self, n_fft=1024, sample_freq = 44100, 
        lower = 30, upper = 4500, maxbirdfreq = 12000):
        self.N_FFT = n_fft
        self.SAMPLE_FREQ = sample_freq
        self.NYQUISTFREQ = sample_freq // 2

        self.LOWFREQ = freqtobin(lower)
        self.UPPERFREQ = freqtobin(upper)
        self.MAXBIRDFREQ = freqtobin(maxbirdfreq)
        #alpha for expotential smoothing from Wikipedia should be
        # 1/NYQUISTFREQ/sample-period 
        self.alpha = N_FFT/SAMPLE_FREQ / 3.0 # average over 3 seconds?
        self.maxPower = 0.0
        
    # create global areas for averaging data
        self.power = numpy.zeros(n_fft)
        self.maxPower = 0.0

    """
    The simplest form of exponential smoothing is given by the formula:

        s(t) = s(t-1) + alpha *_(x(t) - s(t-1))
    
    where alpha is the smoothing factor, and alpha between 0 and 1.

    This does the expotential moving average and then reduces bin values
    by the average sound level in each bin.  
    """

    def averageNoise(self, data):
        tmpMax = 0.0
        for i in range(1, N_FFT-1):
            self.power[i]= self.power[i] + self.alpha * (m.sqrt(pow(abs(data[i]),2)) - self.power[i])
            tmpMax = max(tmpMax, self.power[i])

        self.maxPower = tmpMax + self.alpha * (tmpMax - self.maxPower)
        for i in range(1,N_FFT-1):
            data[i] = data[i] * (1.0 - self.power[i]/self.maxPower)

def main():
    fc = NoiseFilter(1024, 44100, 30, 4500, 12000)

    
    fc.first = True
    for i in range(0, 22050):
        data = np.random.random(1024) + np.random.random(1024) * 1j
        data[0] = 0
        fc.averageNoise(data)
    print("averaged data: ")
    print(abs(data))
    print()


if __name__ == "__main__":
    import numpy as np
    main()