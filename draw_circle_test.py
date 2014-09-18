#! /usr/bin/env python
# -*- coding:utf-8 -*-
#
# written by Shotaro Fujimoto, August 2014.

from Tkinter import *
import numpy as np

def getIndexofcircle(r, x0, y0):
    x = 0; y = r
    D = 3 - 2*r
    Indexofcircle = [(r,0),(0,r),(-r,0),(0,-r)]
    while x < y:
        if D < 0:
            D += 4*x + 6
        else:
            D += 4*x -4*y + 10
            y -= 1
        x += 1
        Indexofcircle += [(y,x),(x,y),(-x,y),(-y,x),
                        (-y,-x),(-x,-y),(x,-y),(y,-x)]
    Indexofcircle = np.array(Indexofcircle) + (x0, y0)
    Indexofcircle = list(set([(m,n) for m,n in Indexofcircle]))
    return Indexofcircle

def draw_canvas(rect, L):
    global canvas
    default_size = 640 # default size of canvas
    r = int(default_size/(2*L))
    if r == 0:
        r = 0.5
    fig_size = 2*r*L
    margin = 10
    sub = Toplevel()

    sub.title('invasion percolation')
    canvas = Canvas(sub, width=fig_size+2*margin,
                height=fig_size+2*margin)
    canvas.create_rectangle(margin, margin,
                fig_size+margin, fig_size+margin,
                outline='black', fill='white')
    canvas.pack()

    c = canvas.create_rectangle

    for m, n in rect:
        c(2*m*r+margin, 2*n*r+margin,
                    2*(m+1)*r+margin, 2*(n+1)*r+margin,
                    outline='black', fill='black')

class TopWindow:

    def quit(self):
        self.root.destroy()
        sys.exit()

    def show_window(self, title="title", *args):
        self.root = Tk()
        self.root.title(title)
        frames = []
        for i, arg in enumerate(args):
            frames.append(Frame(self.root, padx=5, pady=5))
            for k, v in arg:
                Button(frames[i],text=k,command=v).pack(expand=YES, fill='x')
            frames[i].pack(fill='x')
        f = Frame(self.root, padx=5, pady=5)
        Button(f,text='quit',command=self.quit).pack(expand=YES, fill='x')
        f.pack(fill='x')
        self.root.mainloop()

top = TopWindow()
radius = 100
L = 2*radius+1
canvas = None

def pushed():
    circleindex = getIndexofcircle(radius, radius, radius)
    draw_canvas(circleindex, L)
    return circleindex
    
def pr():
    import tkFileDialog
    import os
    
    if canvas is None:
        print "first you should run 'circle'."
        return
    fTyp=[('eps flle','*.eps'), ('all files','*')]
    filename = tkFileDialog.asksaveasfilename(filetypes=fTyp,
                    initialdir=os.getcwd(), initialfile="figure_1.eps")
    if filename == None:
        return
    d = canvas.postscript(file=filename)

top.show_window("Draw Circle Demo", (('circle', pushed),('save to eps file', pr)))

