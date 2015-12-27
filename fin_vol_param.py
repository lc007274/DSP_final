import numpy as np
import pyaudio

p = pyaudio.PyAudio()

CHUNK = 1024            
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

a = RATE / CHUNK * RECORD_SECONDS

volume = 0
frames = []

stream= p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

                
for i in range(int(a)):
    data = stream.read(CHUNK)
    data_int=np.fromstring(data,dtype=np.int)
    data_mod=data_int/(2**24)
    print(data_mod)
    volume += sum(abs(data_mod[0:1024]))
    print(volume)    
        
stream.stop_stream()
stream.close()
p.terminate()
