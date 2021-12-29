# WireFFT
Continuous FFT Filter Development

I have high frequency hearing loss and the frequency responses of my ears 
drop off rapidly after about 4.5kHz. A device, Birders Ear, used to be 
available which divided frenquencies by 2, 3, or 4 as well as offering 
a set of starting frequencies. This was a hardware device, it was 
expensive[$500], and is no longer made [I have a used one from eBay!]. 

My idea was to recreate this hardware device in software Python] -- I knew FFT 
could do the filtering. I had an RPi4 with enough CPU power.  What I didn't realise 
was the RPi audio was very limited and had no input at all. Also, NOBODY, 
it seems, has created a practical realtime/continuous FFT filter. [I suspect
some implementations exist for Ham Radio.]  

After much research, I found Overlap/Add [OLA] [not applicable to continuous 
processing] and decided to implement a continuous OLA so that I could do 
glitchless FFT filtering. My wire.py started-out as the continuous example 
for SoundDevice. I have added code in its Callback routine to handle OLA 
and rfft/irfft. No filtering so far, but that's next. 

I bought a board for audio I/O, and it can improve sampling rates to 96000Hz 
but even at 44100 delays are minimal. [USB devices introduce intolerable 
delays unrelated to sampling rate and are OK for development but useless 
in practice!] My Birders Ear has fantastic stereo 
mics and earphones -- the sound board doesn't support electret mics [it 
has one on-board]. Thus, I'm a fair way from a portable software version of my 
'assist,' but I do have a proof of concept!

One day, perhaps an inexpensive and configurable PyBirdersEar will 
be a realization?
