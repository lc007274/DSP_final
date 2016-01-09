import pyaudio
import time
import numpy as np
import scipy
from Tkinter import *

#123123
# Parameter Definition
RATE  = 4800
DELAY = 900
SOUND_SPEED  = 341.00  # Theoretical sound speed (m/s)
OBJECT_SPEED = -100  # Object moving speed (m/s)

#freq_coeff is the coefficient of the frequency, depends on object speed
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

    
    print("\n\nfreq_coeff = ", "%.2f" % freq_coeff)
    print(" obj speed = ", OBJECT_SPEED)

    stream.start_stream()    
    if stream.is_active():
        sp.after(10, task)
        sp.mainloop()

    p.terminate()
    return

# Keyboard detection
def leftKey(event):
    global OBJECT_SPEED
    print ("Left key pressed")
    OBJECT_SPEED-=1
    print OBJECT_SPEED

def rightKey(event):
    global OBJECT_SPEED
    print ("Right key pressed")
    OBJECT_SPEED+=1
    print OBJECT_SPEED
    
def upKey(event):
    global OBJECT_SPEED
    print ("Up key pressed")
    OBJECT_SPEED+=1
    print OBJECT_SPEED

def upKey2():
    global OBJECT_SPEED
    print ("Up key pressed")
    OBJECT_SPEED+=1
    print OBJECT_SPEED
    
def downKey(event):
    global OBJECT_SPEED
    print ("Down key pressed")
    OBJECT_SPEED-=1
    print OBJECT_SPEED
    
def downKey2():
    global OBJECT_SPEED
    print ("Down key pressed")
    OBJECT_SPEED-=1
    print OBJECT_SPEED

def task():
    spd.set(OBJECT_SPEED)
    frame.pack()
    par.pack(side=LEFT)
    lin.pack(side=LEFT)
    frame.focus_set()
    UP.pack()
    DOWN.pack()
    speed.pack()
    sp.after(10, task)
        
#Tkinker frame

sp = Tk()
frame = Frame(sp)

spd = IntVar()
spd.set(OBJECT_SPEED)

lin = Label(frame, text='object speed')
UP = Button(sp, text=" UP ", command=upKey2)
DOWN = Button(sp, text="DOWN", command=downKey2)
par = Label(frame, textvariable=OBJECT_SPEED)
speed = Button(sp, text = "Present Speed = %s"%(spd.get()))






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

def callback(in_data, frame_count, time_info, status, hl=hl,hr=hr,d=zero_array[:],c=zero_array[:], ):
    
    global OBJECT_SPEED, SOUND_SPEED, freq_coeff, sp
    # Transform byte format in_data to float format out_data
    data_length = int(len(in_data)/4)
    out_data = np.fromstring(in_data,dtype=np.short)
    out_data = out_data/(2.0**15)

    # divide to left&right
    out_data_left=[]
    out_data_right=[]
    
    for i in range(int(len(out_data)/2)):
        out_data_left.extend(out_data[i*2:i*2+1])
        out_data_right.extend(out_data[i*2+1:i*2+2])


    # Fourier Transform
    fft_left = scipy.fft(out_data_left)
    fft_right = scipy.fft(out_data_right)
    out_fft_left = fft_left
    out_fft_right = fft_right


    # Filtering in frequency domain
    FILT_LOW = 1
    FILT_HIGH = data_length;
    fft_left = np.concatenate(([0]*FILT_LOW, fft_left[FILT_LOW:FILT_HIGH], [0]*(data_length-FILT_HIGH)))
    fft_right = np.concatenate(([0]*FILT_LOW, fft_right[FILT_LOW:FILT_HIGH], [0]*(data_length-FILT_HIGH)))

    # Shifting in frequency domain
    FREQ = 0
    if FREQ>0:
        fft_left = np.concatenate(([0]*FREQ, fft_left[:data_length-FREQ]))
        fft_right = np.concatenate(([0]*FREQ, fft_right[:data_length-FREQ]))
    else:
        fft_left = np.concatenate((fft_left[-FREQ:data_length], [0]*(-FREQ)))
        fft_right = np.concatenate((fft_right[-FREQ:data_length], [0]*(-FREQ)))


    # Doopler Effect
    for i in range(data_length):

        # Get the index of original spectrum
        index = np.ceil(i/freq_coeff)

        # Get the ratio of two adjacent component of original spectrum
        low_coeff = index-i/freq_coeff
        high_coeff = 1 - low_coeff

        # Assign to scaled spectrum from linear combination of original spectrum
        if index>data_length-1:
            out_fft_left[i]  = 0.6*out_fft_left[i-1]
            out_fft_right[i] = 0.6*out_fft_right[i-1]
        else:
            out_fft_left[i] = (low_coeff * fft_left[index-1]) + (high_coeff * fft_left[index])
            out_fft_right[i] = (low_coeff * fft_right[index-1]) + (high_coeff * fft_right[index])
#            print( "%.3f" % out_fft_left[i], " = ", "%.1f" % low_coeff, "*", "%.3f" % fft_left[index-1], " / ", "%.1f" % high_coeff, "*", "%.3f" % fft_left[index])

    freq_coeff = SOUND_SPEED/(SOUND_SPEED+OBJECT_SPEED)
    # Inverse Fourier Transform
    out_data_left = scipy.ifft(out_fft_left)
    out_data_right = scipy.ifft(out_fft_right)

    # overlap
    n = len(out_data)
    m = len(hl)
    l = len(out_data_left)

#    print("checkpoint2")
    # put left & right together
    out_data2 = out_data[0:n]
    for i in range(int(len(out_data)/2)):
        out_data2[i*2]   = np.real(out_data_left[i])
        out_data2[i*2+1] = np.real(out_data_right[i])
    
    # Transform float format out_data2 to byte format out
    out_data2 *= 2.0**15
    out = np.int16(out_data2)
    out = out.tostring()

    sp.bind('<Left>', leftKey)
    sp.bind('<Right>', rightKey)
    sp.bind('<Up>', upKey)
    sp.bind('<Down>', downKey)
    
    return (out, pyaudio.paContinue)

main()
