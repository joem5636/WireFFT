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
        self.freqdata = numpy.zeros([self.blocksize, 2])

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
        self.inbuffer[self.blocksize * 2 :] = indata  # append to inbuffer
        self.timedata = self.inbuffer[
            self.blocksize - self.overlap : 
            self.blocksize * 2 + self.overlap, :
        ]

        # expand with loop to do all channels
        for i in range(self.channels - 1):
            # replace timedata with inbuffer[blocksize - overlap:blocksize * 2 + overlap, :]?
            self.channel[:] = self.timedata[:, i] * self.mask
            # do fft
            self.freqdata[:] = numpy.fft.rfft(self.channel)

        return self.freqdata

    def irfft(self, freqdata):
        for i in range(self.channels - 1):
            self.channel = numpy.fft.irfft(freqdata[:, i])
            self.outbuffer[:, i] += self.channel

        self.inbuffer[:-self.blocksize] = self.inbuffer[self.blocksize:]  # left shift inbuffer
        self.inbuffer[-self.blocksize:] = 0  # not really needed for input buffer as replacement is done
    
        self.outbuffer[:-self.overlap] = self.outbuffer[self.overlap:]  # left shift outbuffer
        self.outbuffer[-self.overlap:] = 0  # here, we do a add to the overlap and this zeroed area

        return self.outbuffer[:self.blocksize]