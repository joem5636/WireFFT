"""
This class implements continuous overlap and add with calls to 
numpy.fft.rfft and irfft. This idea is to clean the wireFFT code to 
eliminate the disturbing(?) 'global' statement and crude(?) initialization.

blocksize is the size of the read passed into olafft by the irfft method. 
Blocksize must be a power of 2. Masktype (defaults to Hanning)
is the masking to be used. Masks must be symmetrical and start/stop with 0; 
hence Hanning or Blackman are currently allowed. 

This class assumes stereo. If mono, copy input[:,1]=input[:,0] 
before call. In most cases, stereo out is the same for mono or
stereo. 
"""
import numpy
import math


class olafft:
    
    def __init__(self, blocksize, masktype="hanning"):
        if math.log2(blocksize) % 2 != 0:
            Exception("Blocksize must be a power of 2.")
        self.blocksize = blocksize
        self.overlap = self.blocksize // 2
        
        # create global areas for buffering and processing of channel data
        self.inbuffer = numpy.zeros([self.blocksize * 3, 2])
        self.outbuffer = numpy.zeros([self.blocksize + self.overlap * 2, 2])
        self.timedata = numpy.zeros([self.blocksize + self.overlap * 2, 2])
        self.channel = numpy.zeros([self.blocksize + self.overlap * 2])
        self.freqdata = numpy.zeros([self.blocksize + 1, 2], dtype=numpy.csingle)
        
        self.masktype = None
        
        if masktype != None:
            self.masktype = masktype.lower()
        if (self.masktype == "hanning"
            or self.masktype == "hann"
            or self.masktype == None):
            self.mask = numpy.hanning(
                self.blocksize + self.overlap * 2
            )  
        elif self.masktype == "blackman":
            self.mask = numpy.blackman(
            self.blocksize + self.overlap * 2)  
        else:
            Exception(
                "Mask type, if defined, must be 'Hanning' or 'Blackman'")

    def rfft(self, indata: numpy.array):
        # because of buffering, we introduce a delay of 3 reads before output
        # is clean. indata is [:, 2]
        
        self.inbuffer[self.blocksize * 2:] = indata  # append to inbuffer
        self.timedata = self.inbuffer[
            self.blocksize - self.overlap : 
            self.blocksize * 2 + self.overlap, :
        ]

        # expand with loop to do all channels
        for i in range(2):
            # replace timedata with inbuffer[blocksize - overlap:blocksize * 2 + overlap, :]?
            self.channel[:] = self.timedata[:, i] * self.mask
            # do fft
            self.freqdata[:, i] = numpy.fft.rfft(self.channel)
        
        return self.freqdata

    def irfft(self, freqdata):
    
        for i in range(2):
            self.channel = numpy.fft.irfft(freqdata[:, i])
            self.outbuffer[:, i] += self.channel

        self.inbuffer[:-self.blocksize] = self.inbuffer[self.blocksize:]  # left shift inbuffer
        self.inbuffer[-self.blocksize:] = 0  # not really needed for input buffer as replacement is done
    
        self.outbuffer[:-self.overlap] = self.outbuffer[self.overlap:]  # left shift outbuffer
        # self.outbuffer[-self.overlap:] = 0  # here, we do a add to the overlap and this zeroed area
        return self.outbuffer[:self.blocksize]
    
def main():
    BUFFERSIZE = 1024
    
    ola = olafft(BUFFERSIZE, "Hanning")
    y = numpy.zeros([BUFFERSIZE, 2])
    x = numpy.linspace(numpy.pi, -numpy.pi, 3*BUFFERSIZE)
    freqdata = numpy.zeros([BUFFERSIZE, 2])
    
    for i in range(3):
        
        y[:, 0] = y[:, 1] = numpy.sin(20 * x[i*BUFFERSIZE:(i+1)*BUFFERSIZE])
                     
        freqdata = ola.rfft(y)
        outy = ola.irfft(freqdata)
        
    """
    Input and output will differ since the Hanning filter 
    reduces input values. The reason for the apparent phase 
    shift is not clear.
    """
    plt.style.use('seaborn-poster')
    plt.figure(figsize = (8, 6))
    plt.plot(x[2*BUFFERSIZE:], y[:, 0], label = 'input')
    plt.plot(x[2*BUFFERSIZE:], outy[:, 0], label = 'output')
    plt.ylabel('Amplitude')
    plt.xlabel('Location (x)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    main()