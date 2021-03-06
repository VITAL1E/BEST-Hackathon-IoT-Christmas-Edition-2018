""" based on code from arduino soundlight project """
import pyaudio
import paramiko # ssh tools
import numpy # for fft
import audioop
import sys
import math
import struct
import time
from socket import *

def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print str(i)+'. '+dev['name']
        i += 1
 
def analyze(data, width, sample_rate, bins):
    # Convert raw sound data to Numpy array
    fmt = "%dH"%(len(data)/2)
    data2 = struct.unpack(fmt, data)
    data2 = numpy.array(data2, dtype='h')
 
    # FFT black magic
    fourier = numpy.fft.fft(data2)
    ffty = numpy.abs(fourier[0:len(fourier)/2])/1000
    ffty1=ffty[:len(ffty)/2]
    ffty2=ffty[len(ffty)/2::]+2
    ffty2=ffty2[::-1]
    ffty=ffty1+ffty2
    ffty=numpy.log(ffty)-2
    
    fourier = list(ffty)[4:-4]
    fourier = fourier[:len(fourier)/2]
    
    size = len(fourier)
 
    # Split into desired number of frequency bins
    levels = [sum(fourier[i:(i+size/bins)]) for i in xrange(0, size, size/bins)][:bins]
    
    return levels

def visualize(bins):
    
    # socket setup
    server_host = '192.168.43.35'
    server_port = 2000
    s = socket(AF_INET, SOCK_STREAM) # create TCP socket
    s.connect((server_host, server_port)) 
        

    chunk    = 2048 # Change if too fast/slow, never less than 1024
    scale    = 280   # Change if too dim/bright
    exponent = 2    # Change if too little/too much difference between loud and quiet sounds
    sample_rate = 44100 
    device   = 1  # Change to correct input device; use list_devices()
     
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = sample_rate,
                    input = True,
                    frames_per_buffer = chunk,
                    input_device_index = device)
    
    print "Starting, use Ctrl+C to stop"
    try:
        on = False
        while True:
            data = stream.read(chunk)
            levels = analyze(data, chunk, sample_rate, bins)
            # scale to [0,100]
            for i in range(bins):
                levels[i] = max(min((levels[i]*1.0)/scale, 1.0), 0.0)
                levels[i] = levels[i]**exponent
                levels[i] = int(levels[i]*100)
            
            print levels
            s.send(str(levels))

    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"
        stream.close()
        p.terminate()
        ser.close()
 
if __name__ == '__main__':
    # list_devices()
    visualize(4)
