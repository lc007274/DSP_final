import pyaudio
import time
import numpy as np
import scipy
#123123
# Parameter Definition
RATE  = 20000
DELAY = 900
SOUND_SPEED  = 341   # Theoretical sound speed (m/s)
OBJECT_SPEED = -30    # Object moving speed (m/s)

# freq_coeff is the coefficient of the frequency, depends on object speed
freq_coeff = SOUND_SPEED/(SOUND_SPEED+OBJECT_SPEED)

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
    print("\n\nfreq_coeff = ", "%.2f" % freq_coeff)
    print(" obj speed = ", OBJECT_SPEED)
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
    FREQ = 0
    fft_left = scipy.fft(out_data_left)
    fft_right = scipy.fft(out_data_right)
    out_fft_left = fft_left
    out_fft_right = fft_right

    # Filtering in frequency domain
    FILT_LOW = 1
    FILT_HIGH = 1000;
    fft_left = np.concatenate(([0]*FILT_LOW, fft_left[FILT_LOW:FILT_HIGH], [0]*(1024-FILT_HIGH)))
    fft_right = np.concatenate(([0]*FILT_LOW, fft_right[FILT_LOW:FILT_HIGH], [0]*(1024-FILT_HIGH)))

    # Shifting in frequency domain
    if FREQ>0:
        fft_left = np.concatenate(([0]*FREQ, fft_left[:1024-FREQ]))
        fft_right = np.concatenate(([0]*FREQ, fft_right[:1024-FREQ]))
    else:
        fft_left = np.concatenate((fft_left[-FREQ:1024], [0]*(-FREQ)))
        fft_right = np.concatenate((fft_right[-FREQ:1024], [0]*(-FREQ)))

    for i in range(1024):
        index = np.ceil(i/freq_coeff)
        low_coeff = index-i/freq_coeff
        high_coeff = 1 - low_coeff
        if index>1024:
            out_fft_left[i]=0
            out_fft_right[i]=0
        else:
            out_fft_left[i] = (low_coeff * fft_left[index-1]) + (high_coeff * fft_left[i].real)
            out_fft_right[i] = (low_coeff * fft_right[index-1]) + (high_coeff * fft_right[i])

    # Inverse Fourier Transform
    out_data_left = scipy.ifft(out_fft_left)
    out_data_right = scipy.ifft(out_fft_right)

    # overlap
    n = len(out_data)
    m = len(hl)
    l = len(out_data_left)

    # put left & right together
    out_data2 = out_data[0:n]
    for i in range(int(len(out_data)/2)):
        out_data2[i*2]   = np.real(out_data_left[i])
        out_data2[i*2+1] = np.real(out_data_right[i])
    
    # Transform float format out_data2 to byte format out
    out_data2 *= 2.0**15
    out = np.int16(out_data2)
    out = out.tostring()
    
    return (out, pyaudio.paContinue)

main()
