import soundfile as sf

data, samplerate = sf.read('/home/joem5636/Documents/GitHub/WireFFT/samples/blja2.wav')
sf.write('new_file.flac', data, samplerate)