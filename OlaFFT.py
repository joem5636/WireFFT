"""
This class implements continuous overlap and add with calls to 
numpy.fft.rfft and irfft. This idea is to clean the wireFFT code to 
eliminate the disturbing(?) 'global' statement and crude(?) initialization.

blocksize is the size of the read passed into olafft by the irfft method. 
Blocksize must be a power of 2. Channels (defaults to 1) is the number of 
channels (1 = monoural, 2 = stereo), and masktype (defaults to Hanning)
is the masking to be used. Masks must be symmetrical and start/stop with 0; 
hence Hanning or Blackman are currently allowed. 
"""
import numpy
import math


class olafft:
    
    def __init__(self, blocksize, channels=1, masktype="hanning"):
        if math.log2(blocksize) % 2 != 0:
            Exception("Blocksize must be a power of 2.")
        self.blocksize = blocksize
        self.overlap = self.blocksize // 2

        if channels < 1 or channels > 2:
            Exception("Channels must be 1 - mono, or 2 - stereo")
        else:
            self.channels = channels
        
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

    def rfft(self, indata):
        # because of buffering, we introduce a delay of 3 reads before output
        # is clean.
        
        self.inbuffer[self.blocksize * 2:] = indata  # append to inbuffer
        self.timedata = self.inbuffer[
            self.blocksize - self.overlap : 
            self.blocksize * 2 + self.overlap, :
        ]

        # expand with loop to do all channels
        for i in range(self.channels):
            # replace timedata with inbuffer[blocksize - overlap:blocksize * 2 + overlap, :]?
            self.channel[:] = self.timedata[:, i] * self.mask
            # do fft
            self.freqdata[:, i] = numpy.fft.rfft(self.channel)
        
        return self.freqdata

    def irfft(self, freqdata):
    
        for i in range(0, self.channels-1):
            self.channel = numpy.fft.irfft(freqdata[:, i])
            self.outbuffer[:, i] += self.channel

        self.inbuffer[:-self.blocksize] = self.inbuffer[self.blocksize:]  # left shift inbuffer
        self.inbuffer[-self.blocksize:] = 0  # not really needed for input buffer as replacement is done
    
        self.outbuffer[:-self.overlap] = self.outbuffer[self.overlap:]  # left shift outbuffer
        self.outbuffer[-self.overlap:] = 0  # here, we do a add to the overlap and this zeroed area
        return self.outbuffer[:self.blocksize]
    
def main():
    BUFFERSIZE = 1024
    ola = olafft(BUFFERSIZE, 2, "hanning")
    y = numpy.zeros([BUFFERSIZE, 2])
    for i in range(200):
        x = numpy.linspace(0, 20, BUFFERSIZE)
        y[:, 0] = y[:, 1] = numpy.sin(x)
             
        freqdata = ola.rfft(y)
        outy = ola.irfft(freqdata)
        
    """
    Input and output will differ since:
        a. The Hanning filter reduces input values
        b. My overlap at 1023 to 0 of the next 'frame'
            was just a guess and appears to be wrong. 
            Another possibility is the Overlap/Add is off
            by one?
    """
    plt.style.use('seaborn-poster')
    plt.figure(figsize = (8, 6))
    plt.plot(x, y[:, 0], label = 'input')
    plt.plot(x, outy[:, 0], label = 'output')
    plt.ylabel('Amplitude')
    plt.xlabel('Location (x)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    main()