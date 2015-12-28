from Tkinter import *

main = Tk()
speed = 0

def leftKey(event):
    global speed
    print "Left key pressed"
    speed-=1
    print speed

def rightKey(event):
    global speed
    print "Right key pressed"
    speed+=1
    print speed
    
def upKey(event):
    global speed
    print "Up key pressed"
    speed+=1
    print speed

def downKey(event):
    global speed
    print "Down key pressed"
    speed-=1
    print speed


frame = Frame(main, width=100, height=100)
main.bind('<Left>', leftKey)
main.bind('<Right>', rightKey)
main.bind('<Up>', upKey)
main.bind('<Down>', downKey)
#frame.focus_set()
frame.pack()
main.mainloop()