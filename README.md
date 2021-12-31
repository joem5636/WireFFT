# WireFFT
Continuous FFT Filter Development

I have high frequency hearing loss and the frequency response of my ears 
drop off rapidly after about 4.5kHz. A device, Birders Ear, used to be 
available which divided frequencies by 2, 3, or 4 as well as offering 
a set of starting frequencies [high, medium, low?]. This is a hardware device 
implementing the transformation in chips (with embedded code?), it was 
expensive [~$500], and is no longer made [I have a used one from eBay!]. 

My idea was to recreate this hardware device in software [Python] -- I knew FFT 
could do the filtering. I had an RPi4+ with enough CPU power.  What I didn't realise 
was the RPi audio was very limited and had no audio input at all. Also, NOBODY -- 
it seems, has created a practical realtime/continuous FFT filter in software. 
[I suspect some implementations exist for Ham Radio.]  

After much research, I found the Overlap/Add technique [OLA] but found it 
was not applicable to continuous processing. I decided to implement a 
continuous OLA so that I could do FFT filtering with no glitches. My wireFFT.py 
started-out as the continuous input/output example for SoundDevice as example 
wire.py. I have added code in its Callback routine to handle OLA 
and rfft/irfft. [My feeling is that my approach is not elegant -- perhaps 
make it a class?] No filtering so far, but that is next, and I already have 
various divide-by and compression schemes implemented. 

I bought an addon board for audio I/O -- Audio Injector Stereo SoundCard, 
-- with stereo I/O and an on-board electret microphone for monoral input. 
It can improve sampling rates to 96000Hz but even at the default 44100 sampling
delays are minimal. [USB devices are cheap but introduce intolerable delays 
unrelated to sampling rate and are OK for development but useless in practice!] 
My Birders Ear has fantastic stereo electret mics and Sony earphones -- the 
SoundCard doesn't support external electret mics [it has one on-board]. Thus, 
I'm a fair way from a portable software version of my 'hearing assist,' but 
I do have a proof of concept!

One day, perhaps a pocketable, inexpensive, and configurable PyBirdersEar will 
be a realization?
