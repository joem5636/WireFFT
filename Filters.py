#!/usr/bin/env python3

"""
This class implements various filters. Folding divides high 
frequencies and adds their value to lower (audible?) frequencies. 

Compression 'squeezes' frequency data from the low limit FOLDFREQ (20, 100Hz?) 
up to the limit of bird song (supposedly 12kHz) into the audible 
range defined by UPPERFREQ. Two forms of compression are defined: linear
takes equal sized groups of bins and adds their content to the 
output. Nonlinear does the same thing but with groups starting at 1 bin
and growing as defined so that the last group goes into the UPPERFREQ bin. 

Not implemented, but similar to folding would be to provide frequency
division by 2, 3, or 4 as in the hardware SongFinder.

A possible improvement might be to do the compression grouping 
proportionately. Just a guess -- I suspect the difference will be 
inaudible. 
"""
import math as m


N_FFT = 1024
SAMPLE_FREQ = 44100 # typical sampling frequency
NYQUISTFREQ = SAMPLE_FREQ // 2  # Nyquist Frequency

def freqtobin(freq):
    return int((N_FFT - 1) * freq / NYQUISTFREQ + 0.5) + 1

LOWFREQ = freqtobin(30)  # lower limit for hearing range
UPPERFREQ = freqtobin(4500)  # upper limit for hearing range
MAXBIRDFREQ = freqtobin(12000)
multiplier = 1.0
adder = 1.0
wrap = 1

class Filters(object):
    def __init__(self, n_fft=1024, sample_freq = 44100, 
        lower = 30, upper = 4500, maxbirdfreq = 12000):
        self.N_FFT = n_fft
        self.SAMPLE_FREQ = sample_freq
        self.NYQUISTFREQ = sample_freq // 2

        self.LOWFREQ = freqtobin(lower)
        self.UPPERFREQ = freqtobin(upper)
        self.MAXBIRDFREQ = freqtobin(maxbirdfreq)

        self.first = False
        self.wrap = UPPERFREQ - LOWFREQ + 1
        self.multiplier = m.pow((MAXBIRDFREQ - LOWFREQ + 1), 1 / (UPPERFREQ - LOWFREQ + 1))
        self.adder = int((MAXBIRDFREQ - LOWFREQ + 1)/(UPPERFREQ - LOWFREQ + 1))

    def fold(self, data): 
        # data is assumed to be frequency data from a single-sided
        # fft such as rfft. Currently, it is for a single channel. 
        
        # in one pass we compress all frequencies higher than foldfreq to the range
        # foldfreq to upperfreq skipping DC (0 frequency) component
        # folding
        if self.first:
            print(data.shape)
            self.first = False

        for i in range(self.UPPERFREQ, self.MAXBIRDFREQ):
            data[self.LOWFREQ + (i % self.wrap)] += data[i]
            data[i] = 0
        data[self.MAXBIRDFREQ + 1:] = 0


    def linear(self, data):
        # linear compression ((b-a)*(x - min))//(max - min) + a
        # b = upper, a=fold, max = NFREQ, min = 0 (or 1?)
        if self.first:
            print(data.shape)
            self.first = False

        for i in range(self.LOWFREQ, self.MAXBIRDFREQ):
            icomp = ((self.UPPERFREQ - self.LOWFREQ) * i) // (self.MAXBIRDFREQ - self.LOWFREQ) + self.LOWFREQ - 1
            data[icomp] += data[i]
            data[i] = 0
        
        data[self.MAXBIRDFREQ + 1:] = 0

    def nonlinear(self, data):
        # log scaling
        # EXAMPLE
        #   Given the values on the linear NFREQ range from fold to NFREQ,
        #   and the values on the logarithmic scaled axis range from
        #   fold to upper, and the log base is 10.
        #   Given x, what is y?
        #
        #   Rearranging equation to solve for 'y' yields,
        #    y = int(exp (x - fold)/(NFREQ - fold) * (log(upper) - log(fold)) + log(fold))
        #    y for x=fold should be fold
        #    y for x=NFREQ should be upper
        #
        if self.first:
            print(data.shape)
            self.first = False

        x = 1.0
        start = int(x)
        r1 = self.LOWFREQ

        for i in range(self.LOWFREQ, self.UPPERFREQ):

            r0 = max(i, r1)
            r1 = min(self.MAXBIRDFREQ, max(int(x) + self.LOWFREQ - 1, r0))

            for icomp in range(r0, r1):
                if i != icomp:
                    data[i] += data[icomp]
                    data[icomp] = 0

            start = int(x)
            x *= self.multiplier
            if x > self.MAXBIRDFREQ - self.LOWFREQ:
                break
        data[self.MAXBIRDFREQ + 1:] = 0 # zero rest of frequency data


def main():
    fc = Filters(1024, 44100, 30, 4500, 12000)

    data = np.arange(0, 1024)
    fc.first = True
    fc.fold(data)
    print("folded data: ")
    print(data[:freqtobin(4500)])
    print()

    data = np.arange(0, 1024)
    fc.first = True
    fc.linear(data)
    print("linear compression data: ")
    print(data[:freqtobin(4500)])
    print()

    data = np.arange(0, 1024)
    fc.first = True
    fc.nonlinear(data)
    print("nonlinear compression data: ")
    print(data[:freqtobin(4500)])

if __name__ == "__main__":
    import numpy as np
    main()