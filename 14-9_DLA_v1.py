#! /usr/bin/env python 
# -*- coding:utf-8 -*-
#
# written by Shotaro Fujimoto, August 2014. 

from Tkinter import *
import numpy as np
import matplotlib.pyplot as plt
import random
import sys
import time

class DLA(object):

    def __init__(self, N, view=True, color=True):
        self.r = 3
        self.N = N
        self.view = view
        self.color = color
        self.L = int(self.N**(0.78))
        
        if self.view:
            self.default_size = 640 # default size of canvas
            self.rsize = int(self.default_size/(2*self.L))
            if self.rsize == 0:
                self.rsize = 1
            fig_size = 2*self.rsize*self.L
            self.margin = 10
            self.sub = Toplevel()
            self.canvas = Canvas(self.sub, width=fig_size+2*self.margin,
                        height=fig_size+2*self.margin)
            self.c = self.canvas.create_rectangle
            self.update = self.canvas.update

            self.sub.title('DLA cluster')
            self.c(self.margin, self.margin,
                        fig_size+self.margin, fig_size+self.margin,
                        outline='black', fill='white')
            self.canvas.pack()
            self.start_time = time.time()
        
    def getIndexofcircle(self, r, x0, y0):
        """中心座標(x0, y0)，半径rの円の円周上の座標を返す．
        Michener's algorithm
        """
        x = 0
        y = r
        D = 3 - 2*r
        Indexofcircle = [(r, 0), (0, r), (-r, 0), (0, -r)]
        while x < y:
            if D < 0:
                D += 4*x + 6
            else:
                D += 4*x -4*y + 10
                y -= 1
            x += 1
            Indexofcircle += [(y, x), (x, y), (-x, y), (-y, x),
                              (-y, -x), (-x, -y), (x, -y), (y, -x)]
        Indexofcircle = np.array(Indexofcircle) + (x0, y0)
        Indexofcircle = list(set([(m,n) for m,n in Indexofcircle]))
        return Indexofcircle

    def grow_cluster(self):
        lattice = np.zeros([self.L*2+1, self.L*2+1], dtype=int)
        # 種の格子点
        self.center = self.L
        lattice[self.center, self.center] = 1
        if self.view:
            c = self.c
            rect = c((2*self.center-self.L)*self.rsize+self.margin,
                        (2*self.center-self.L)*self.rsize+self.margin,
                        (2*(self.center+1)-self.L)*self.rsize+self.margin-1,
                        (2*(self.center+1)-self.L)*self.rsize+self.margin-1,
                        outline='black', fill='black')
        
        rn = np.random.rand
        choice = random.choice
        
        def reset():
            """初期点の選択"""
            start = choice(self.innercircle)
            return start[0], start[1]
        
        def circle_update():
            self.innercircle = self.getIndexofcircle(self.r+2,
                                                     self.center, self.center)
        
        circle_update()
        x, y = reset()
        n = 0
        l = 1
        while n < self.N:
            
            # クラスターの周辺から遠いところでは歩幅を大きくする
            r = np.sqrt((x-self.center)**2+(y-self.center)**2)
            if r > self.r+2:
                l = int(r-self.r-2)
                if l == 0: l = 1
            else: l = 1
            
            p = rn()*4
            if   p < 1: x += l
            elif p < 2: x -= l
            elif p < 3: y += l
            else:       y -= l
            
            r = np.sqrt((x-self.center)**2+(y-self.center)**2)
            if r >= 2*self.r:
                x, y = reset()
                continue
            judge = np.sum(lattice[x-1,y]+lattice[x+1,y]
                        +lattice[x,y-1]+lattice[x,y+1])
            # 粒子をクラスターに取り込む
            if judge > 0:
                lattice[x, y] = 1
                # 描画
                if self.view:
                    if self.color:
                        colors = ['#ff0000', '#ff8000', '#ffff00', '#80ff00',
                                  '#00ff00', '#00ff80', '#00ffff', '#0080ff', 
                                  '#0000ff', '#8000ff', '#ff00ff', '#ff0080']
                        color = colors[int(n/100)%len(colors)]
                    else:
                        color = "black"
                    rect = c((2*x-self.L)*self.rsize+self.margin,
                                    (2*y-self.L)*self.rsize+self.margin,
                                    (2*(x+1)-self.L)*self.rsize+self.margin-1,
                                    (2*(y+1)-self.L)*self.rsize+self.margin-1,
                                    outline=color, fill=color)
                    self.update()
                # rmaxの更新
                if int(r)+1 > self.r:
                    self.r = int(r) + 1
                    circle_update()
                x, y = reset()
                n += 1
        else:
            if self.view:
                self.end_time = time.time()
                t = self.end_time-self.start_time
                print "done; N = %d, time = " % self.N + str(t) + ' (s)' 
        return lattice
        
class SetParameter():

    def show_setting_window(self, parameters, commands):
        """ Show a parameter setting window.
                
        parameters: A list of dictionaries {'parameter name': default_value}
        commands: A list of dictionary {'name of button': command}
        """
        self.root = Tk()
        self.root.title('Parameter')
        
        frame1 = Frame(self.root, padx=5, pady=5)
        frame1.pack(side='top')
        self.entry = []
        for i, parameter in enumerate(parameters):
            label = Label(frame1, text=parameter.items()[0][0] + ' = ')
            label.grid(row=i, column=0, sticky=E)
            self.entry.append(Entry(frame1, width=10))
            self.entry[i].grid(row=i, column=1)
            self.entry[i].delete(0, END)
            self.entry[i].insert(0, parameter.items()[0][1])
        self.entry[0].focus_set()
       
        frame2 = Frame(self.root, padx=5, pady=5)
        frame2.pack(side='bottom')
        self.button = []
        for i, command in enumerate(commands):
            self.button.append(Button(frame2, text=command.items()[0][0],
                                      command=command.items()[0][1]))
            self.button[i].grid(row=0, column=i)
        
        self.root.mainloop()

class Main(object):

    def __init__(self):
        self.sp = SetParameter()
        self.count = 1
        self.dla = None
        self.sp.show_setting_window([{'N': 200}],
                        [{'a': self.exp_a},{'b': self.exp_b},{'c': self.exp_c},
                         {'save': self.pr},{'quit':sys.exit}])
        
    def exp_a(self):
        self.N = int(self.sp.entry[0].get())
        self.dla = DLA(self.N)
        lattice = self.dla.grow_cluster()
    
    def exp_b(self):
        trial = 3000
        self.dla2 = DLA(2, view=False)
        self.dla2.L = 6
        distribution = {'p': 0, 'q': 0, 'r': 0, 's': 0}
        for i in range(trial):
            lattice = self.dla2.grow_cluster()
            l = lattice[self.dla2.L-1:self.dla2.L+2,
                        self.dla2.L-1:self.dla2.L+2]
            if np.sum(l) == 2:
                distribution['r'] += 1
            elif np.sum(l[0,1]+l[1,0]+l[1,2]+l[2,1]) == 1:
                distribution['p'] += 1
            elif max(max(np.sum(l, 0)), max(np.sum(l, 1))) == 3:
                distribution['s'] += 1
            else:
                distribution['q'] += 1
        for k, v in distribution.items():
            distribution[k] = float(v)/trial
        distribution['p'] = distribution['p']/2.
        distribution['q'] = distribution['q']/2.
        print 'trial = %d' % trial
        print distribution
    
    def exp_c(self):
        self.N = int(self.sp.entry[0].get())
        self.dla3 = DLA(self.N, view=False)
        self.lattice = self.dla3.grow_cluster()
        self.view_expansion()
        filename = 'data.txt'
        data = np.array([self.b, self.M_b])
        np.savetxt(filename, data, delimiter=', ')
        self.plot()
    
    def view_expansion(self):
        lattice = self.lattice
        center = self.dla3.center
        M_b = []
        s = np.sum
        ave = np.average
        append = M_b.append
        for k in range(1, center):
            nonzero = np.nonzero(lattice[k:-k,k:-k])
            tmp = np.array([0])
            for i, j in zip(nonzero[0]+k, nonzero[1]+k):
                tmp = np.append(tmp, s(lattice[i-k:i+k+1, j-k:j+k+1]))
            append(ave(tmp))
        self.b = np.array([2.*k+1 for k in range(1, center)])
        self.M_b = np.array(M_b)
    
    def plot(self):
        fig = plt.figure("Fractal Dimesion")
        ax = fig.add_subplot(111)
        ax.plot(self.b, self.M_b, '-o')
        ax.set_xlabel(r'$b$', fontsize=16)
        ax.set_ylabel(r'$M(b)$', fontsize=16)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_ymargin(0.05)
        fig.tight_layout()
        plt.show()

    def pr(self):
        if self.dla is None:
            print "first you should run 'a'."
        else:
            d = self.dla.canvas.postscript(file="figure_%d.eps" % self.count)
            print "saved the figure to a eps file"
            self.count += 1
    
if __name__ == '__main__':

    Main()
    
