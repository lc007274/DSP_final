import pyaudio
import time
import numpy as np
import scipy
#123123
# Parameter Definition
RATE  = 20000
DELAY = 900
SOUND_SPEED  = 341   # Theoretical sound speed (m/s)
OBJECT_SPEED = 0    # Object moving speed (m/s)

# freq_coeff is the coefficient of the frequency, depends on object speed
freq_coeff = SOUND_SPEED/(SOUND_SPEED+OBJECT_SPEED)
print("freq_coeff = ", freq_coeff)

# Main function
def main():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=RATE,
                    input=True,
                    output=True,
                    stream_callback=callback)

    stream.start_stream()
    while stream.is_active():
        time.sleep(0.2)

    p.terminate()
    return


# hl is a unit impulse function
hl = []
hl.extend([1])
hl.extend([0]*DELAY)

# hr is a delay impulse function
hr = []
hr.extend([0]*DELAY)
hr.extend([1])

zero_array=[]
zero_array.extend([0]*len(hl))

def callback(in_data, frame_count, time_info, status, hl=hl,hr=hr,d=zero_array[:],c=zero_array[:]):

    # Transform byte format in_data to float format out_data
    out_data = np.fromstring(in_data,dtype=np.short)
    out_data = out_data/(2.0**15)

    # divide to left&right
    out_data_left=[]
    out_data_right=[]
    
    for i in range(int(len(out_data)/2)):
        out_data_left.extend(out_data[i*2:i*2+1])
        out_data_right.extend(out_data[i*2+1:i*2+2])

    # Fourier Transform
    FREQ = -12
    fft_left = scipy.fft(out_data_left)
    fft_right = scipy.fft(out_data_right)

    # Shifting in frequency domain
    if FREQ>0:
        fft_left = np.concatenate(([0]*FREQ, fft_left[:1024-FREQ]))
        fft_right = np.concatenate(([0]*FREQ, fft_right[:1024-FREQ]))
    else:
        fft_left = np.concatenate((fft_left[-FREQ:1024], [0]*(-FREQ)))
        fft_right = np.concatenate((fft_right[-FREQ:1024], [0]*(-FREQ)))

    # Inverse Fourier Transform
    out_data_left = scipy.ifft(fft_left)
    out_data_right = scipy.ifft(fft_right)

    # overlap
    n = len(out_data)
    m = len(hl)
    l = len(out_data_left)

    # put left & right together
    out_data2 = out_data[0:n]
    for i in range(int(len(out_data)/2)):
        out_data2[i*2]   = out_data_left[i]
        out_data2[i*2+1] = out_data_right[i]
    
    # Transform float format out_data2 to byte format out
    out_data2 *= 2.0**15
    out = np.int16(out_data2)
    out = out.tostring()
    
    return (out, pyaudio.paContinue)

main()
