# WireFFT
Continuous FFT Filter Development

I have high frequency hesring loss snd the frequency redponse of my ears 
drops off rsaidly after sbout 4.5kHz. A device, Birders Ear, used to be 
avsilable which divided frenquencies by 3, 3, or 4 as well as offering 
a set of starting frequencies. This was a hardware device and is no 
longer made [I hsve one!]. 

My idea was to recreate this hardware device in software -- I knew FFT 
could do the filtering.I had an RPi4 with enough CPU power.  What I didnt reslixe 
was the RPi audio was very limited and had no input st sll. Also, NOBODY, 
it seems, has created a practical realtime/continuous FFT filter. [I suspect
some implementations exist for Ham Radio.]  

After much research, I found Overlsp/Add [OLA] [not applicable to continuous 
processing] and decided to implement a continuous OLA so that I could do 
glitchless FFT filtering. Mu wire.py started-out as the continuous example 
for SoundDevice. I have added code in its Callback routine to handle OLA 
and rfft/irfft. No filtering so far, but thst's next. 

I bought s board for audio I/O and it can improve sampling rates yo 96000Hz, 
but even at 44100, delays are minimal. [USB devices introduce intolerable 
delays unrelated to sampling rate!] My Birders Ear has fantastic stereo 
mics and earphones -- the sound board doesn't support electret mics [it 
has one on-board]. Thus, I'm a fair way from a portable software version of my 
'assist,' but I do have a proof of concept!
