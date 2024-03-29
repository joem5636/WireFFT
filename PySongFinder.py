#!/usr/bin/env python3
"""Pass input directly to output using classed OlaFFT and with filtering.
"""
# import debugpy # needed only for debugging in threads


import argparse

import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
import OlaFFT
import Filters
import NoiseFilter

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-i', '--input-device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-o', '--output-device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-c', '--channels', type=int, default=2,
    help='number of channels')
parser.add_argument('--dtype', help='audio data type')
parser.add_argument('--samplerate', type=float, help='sampling rate', default=44100)
parser.add_argument('--blocksize', type=int, help='block size', default=1024)
parser.add_argument('--latency', type=float, help='latency in seconds')
args = parser.parse_args(remaining)

first = True
parser.parse_args()  # needed to prevent blocksize from being 'none' in overlap computation
blocksize = args.blocksize
samplerate = args.samplerate

freqdata = numpy.zeros([blocksize, 2])

olaFFT = OlaFFT.olafft(blocksize) # define class
filter = Filters.Filters(blocksize, samplerate, lower=30, upper=4500)
noiseFilter = NoiseFilter.NoiseFilter(blocksize, samplerate, lower=30, upper=4500)



def callback(indata, outdata, frames, time, status):
    
    # debugpy.debug_this_thread() # needed only for debugging in threads
    global freqdata
    freqData = olaFFT.rfft(indata)
    freqData[0] = 0
    noiseFilter.averageNoise(freqData[ : , 0]) # channel 0
    filter.fold(freqData[ : , 0]) # channel 0 
    outdata[:] = olaFFT.irfft(freqData)    

try:
    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=args.samplerate, blocksize=args.blocksize,
                   dtype=args.dtype, latency=args.latency,
                   channels=args.channels, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    parser.exit('')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))