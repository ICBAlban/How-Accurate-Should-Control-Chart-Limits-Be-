import tkinter as tk
from tkinter.font import Font
from tkinter.messagebox import showerror, showwarning
from tkinter.filedialog import askopenfilename
from os import path
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from tkinter.ttk import Progressbar
from tkinter.colorchooser import askcolor
from math import sqrt

def A_E(d2, d3, c4, n:int=2, k:float=3):
    A2 = k/(d2*sqrt(n))
    A3 = k/(c4*sqrt(n))
    B3 = 1-(k/c4)*np.sqrt(1-np.power(c4, 2)) 
    B3 = 0 if B3<0 else B3
    B4 = 1+(k/c4)*np.sqrt(1-np.power(c4, 2))
    B5 = c4-k*np.sqrt(1-np.power(c4, 2))
    B5 = 0 if B5<0 else B5
    B6 = c4+k*np.sqrt(1-np.power(c4, 2))
    D1 = d2-k*d3
    D1 = 0 if D1<0 else D1
    D2 = d2+k*d3
    D3 = 1-k*d3/d2
    D3 = 0 if D3<0 else D3
    D4 = 1+k*d3/d2
    return [A2, A3, B3, B4, B5, B6, D1, D2, D3, D4]


def d2_d3_c4(n_ite, n):
    A = np.random.normal(0, 1, (n_ite, n))
    r= np.zeros((n_ite))
    for i in range(n_ite):
        r[i] = (max(A[i,:])-min(A[i,:]))
    d2 = np.mean(r)
    d3 = np.std(r)
    c4 = np.mean(np.std(A, axis = -1, ddof=1))
    return [d2, d3, c4]

class fn:
    def __init__(self, fn, X:list, Y:list, moy:float, LSL:float, USL:float,
                 title:str="Result"):
        
        self._col_3_sigma = "#880015"
        self._col_2_sigma = "#ED1C24"
        self._col_1_sigma = "#FF7F27"

        self._X = X
        self._Y = Y
        self._moy = moy
        self._LSL = LSL
        self._USL = USL
        self._fn = tk.Toplevel(fn)
        self._var_regle = tk.StringVar()
        self._fn.title(title)
        self._fn.resizable(width=False, height=False)
        self._creation_fn()
        self._plot_configure()

    def _creation_fn(self):
        label = tk.LabelFrame(self._fn, text="Rules : ")
        label.grid(row=0, column=0)
        L_text = [" ; Large shift analysis: 1 or more points     \nmore than 3σ from the mean                  ",
                  " ; Large shift analysis: 2 of 3 consecutive   \npoints between 2σ and 3σ from the mean      ",
                  " ; Smaller shift and trends analysis:         \n4 of 5 consecutive points between 1σ and 3σ \nfrom the mean",
                  " ; Smaller shift analysis: 8 consecutive      \npoints on one side of the mean              ",
                  " ; Trends analysis: 6 consecutive points      \nsteadily increasing or decreasing           ",
                  " ; Stratification analysis: 15 consecutive    \npoints both above and below central line    ",
                  " ; Systematic variation analysis: 14          \nconsecutive points alternating up and down  ",
                  " ; Mixture analysis: 8 points in a row on     \nboth sides of the centre line upper than 1σ "]

        for i in range(8):
            r = tk.Radiobutton(label, text="Rule "+str(i+1) + L_text[i], value=i, variable=self._var_regle)
            r.grid(row=i, column=0, sticky="W")

        self._var_regle.set(0)

        bout = tk.Button(label, text="View", command=self._visualiser_resultat)
        bout.grid(row=8, column=0, sticky="NEWS")

        label = tk.Frame(self._fn)
        label.grid(row=0, column=1) 
        self._fig = Figure(figsize=(4,4)) 
        self._plot = self._fig.add_subplot(111)
        self._plot.plot(self._X, self._Y, "--xk")
        L = [np.min(self._X), np.max(self._X)]
        self._plot.plot(L, [self._USL, self._USL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*2/3, 
                            self._moy+(self._USL-self._moy)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*1/3, 
                            self._moy+(self._USL-self._moy)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._LSL, self._LSL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy-(self._moy-self._LSL)*2/3, 
                            self._moy-(self._moy-self._LSL)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy-(self._moy-self._LSL)*1/3, 
                            self._moy-(self._moy-self._LSL)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._moy, self._moy], "-k")
        
        #self._plot.set_axis_off()     
        self._fig.subplots_adjust(left=0.2)
        self._canvas = FigureCanvasTkAgg(self._fig, master = label)   
        self._canvas.draw()
        label_2 = tk.Frame(label)
        label_2.grid(row=2, column=0, sticky='W') 
        NavigationToolbar2Tk(self._canvas, label_2).update()

        self._canvas.get_tk_widget().grid(row=1, column=0)

    def _plot_configure(self):
        label = tk.LabelFrame(self._fn, text="Graph parameters: ")
        label.grid(row=0, column=2)

        texte = tk.Label(label, text = 'Title:')
        texte.grid(row=0, column=0, sticky="E")
        self._entree_title = tk.Entry(label, width=15)
        self._entree_title.insert(0, "")
        self._entree_title.grid(row=0, column=1, sticky="E")
        self._entree_title.bind("<Key>", self._afficher_plot_event)
        self._entree_title.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_title.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'x label:')
        texte.grid(row=1, column=0, sticky="E")
        self._entree_xlabel = tk.Entry(label, width=15)
        self._entree_xlabel.insert(0, "")
        self._entree_xlabel.grid(row=1, column=1, sticky="E")
        self._entree_xlabel.bind("<Key>", self._afficher_plot_event)
        self._entree_xlabel.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_xlabel.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'y label:')
        texte.grid(row=2, column=0, sticky="E")
        self._entree_ylabel = tk.Entry(label, width=15)
        self._entree_ylabel.insert(0, "")
        self._entree_ylabel.grid(row=2, column=1, sticky="E")
        self._entree_ylabel.bind("<Key>", self._afficher_plot_event)
        self._entree_ylabel.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_ylabel.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Minimal x limit:')
        texte.grid(row=3, column=0, sticky="E")
        self._entree_lim_min_x = tk.Entry(label, width=8)
        self._entree_lim_min_x.insert(0, str(round(self._fig.gca().get_xlim()[0], 3)))
        self._entree_lim_min_x.grid(row=3, column=1, sticky="E")
        self._entree_lim_min_x.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_min_x.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_min_x.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Maximal x limit:')
        texte.grid(row=4, column=0, sticky="E")
        self._entree_lim_max_x = tk.Entry(label, width=8)
        self._entree_lim_max_x.insert(0, str(round(self._fig.gca().get_xlim()[1], 3)))
        self._entree_lim_max_x.grid(row=4, column=1, sticky="E")
        self._entree_lim_max_x.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_max_x.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_max_x.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Minimal y limit:')
        texte.grid(row=5, column=0, sticky="E")
        self._entree_lim_min_y = tk.Entry(label, width=8)
        self._entree_lim_min_y.insert(0, str(round(self._fig.gca().get_ylim()[0], 3)))
        self._entree_lim_min_y.grid(row=5, column=1, sticky="E")
        self._entree_lim_min_y.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_min_y.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_min_y.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Maximal y limit:')
        texte.grid(row=6, column=0, sticky="E")
        self._entree_lim_max_y = tk.Entry(label, width=8)
        self._entree_lim_max_y.insert(0, str(round(self._fig.gca().get_ylim()[1], 3)))
        self._entree_lim_max_y.grid(row=6, column=1, sticky="E")
        self._entree_lim_max_y.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_max_y.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_max_y.bind("<Leave>", self._afficher_plot_event)

        self._bout_3s = tk.Button(label, text = 'Color of 3σ limit:', 
                                  command=self._couleur_3_limites)
        self._bout_3s.configure(bg=self._col_3_sigma)
        self._bout_3s.grid(row=7, column=0, columnspan=2, sticky="WESN")

        self._bout_2s = tk.Button(label, text = 'Color of 2σ limit:', 
                                  command=self._couleur_2_limites)
        self._bout_2s.configure(bg=self._col_2_sigma)
        self._bout_2s.grid(row=8, column=0, columnspan=2, sticky="WESN")

        self._bout_1s = tk.Button(label, text = 'Color of 1σ limit:', 
                                  command=self._couleur_1_limites)
        self._bout_1s.configure(bg=self._col_1_sigma)
        self._bout_1s.grid(row=9, column=0, columnspan=2, sticky="WESN")

    def _afficher_plot_event(self, event):
        self._visualiser_resultat()

    def _couleur_3_limites(self):
        self._col_3_sigma = askcolor(title="Color of 3σ limit")[1]
        self._bout_3s.configure(bg=self._col_3_sigma)
        self._visualiser_resultat()

    def _couleur_2_limites(self):
        self._col_2_sigma = askcolor(title="Color of 2σ limit")[1]
        self._bout_2s.configure(bg=self._col_2_sigma)
        self._visualiser_resultat()

    def _couleur_1_limites(self):
        self._col_1_sigma = askcolor(title="Color of 1σ limit")[1]
        self._bout_1s.configure(bg=self._col_1_sigma)
        self._visualiser_resultat()

    def _visualiser_resultat(self):
        try:
            self._afficher_plot()

            if int(self._var_regle.get())==0:
                X, Y = self._regle_1(self._LSL, self._USL)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==1:
                X, Y = self._regle_2(self._moy-(self._moy-self._LSL)*2/3, self._moy+(self._USL-self._moy)*2/3)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==2:
                X, Y = self._regle_3(self._moy-(self._moy-self._LSL)/3, self._moy+(self._USL-self._moy)/3)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==3:
                X, Y = self._regle_4(self._moy, self._moy)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==4:
                X, Y = self._regle_5()
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==5:
                X, Y = self._regle_6()
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==6:
                X, Y = self._regle_7()
                self._plot.plot(X, Y, "or")
            else:
                X, Y = self._regle_8(self._moy-(self._moy-self._LSL)/3, 
                                     self._moy+(self._USL-self._moy)/3)
                self._plot.plot(X, Y, "or")

            self._canvas.draw()
            self._fn.update_idletasks()
        except:
            showwarning("Problem", "Drawing")

    def _afficher_plot(self):
        self._plot.cla()

        self._plot.plot(self._X, self._Y, "--xk")
        L = [np.min(self._X), np.max(self._X)]
        self._plot.plot(L, [self._USL, self._USL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*2/3, 
                            self._moy+(self._USL-self._moy)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*1/3, 
                            self._moy+(self._USL-self._moy)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._LSL, self._LSL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy-(self._moy-self._LSL)*2/3, 
                            self._moy-(self._moy-self._LSL)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy-(self._moy-self._LSL)*1/3, 
                            self._moy-(self._moy-self._LSL)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._moy, self._moy], "-k")

        self._plot.set_ylim([float(self._entree_lim_min_y.get()), 
                             float(self._entree_lim_max_y.get())])

        self._plot.set_xlim([float(self._entree_lim_min_x.get()), 
                             float(self._entree_lim_max_x.get())])
        
        self._plot.set_xlabel(self._entree_xlabel.get())
        self._plot.set_ylabel(self._entree_ylabel.get())
        self._plot.set_title(self._entree_title.get())
        self._canvas.draw()
        self._fn.update_idletasks()

    def _regle_1(self, LSL, USL):
        X_f = []
        Y_f = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_f.append(self._X[i])
                Y_f.append(self._Y[i])
            if self._Y[i] < LSL:
                X_f.append(self._X[i])
                Y_f.append(self._Y[i])
        return X_f, Y_f

    def _regle_2(self, LSL, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>2:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=2:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p.pop(0)
                    Y_p.pop(0)
            
            if self._Y[i] < LSL:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>2:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >=2:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m.pop(0)
                    Y_m.pop(0)

        return X_f, Y_f

    def _regle_3(self, LSL, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>4:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=4:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
            
            if self._Y[i] < LSL:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>4:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >=4:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m = []
                    Y_m = []

        return X_f, Y_f
    
    def _regle_4(self, LSL, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>8:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=8:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
            
            if self._Y[i] < LSL:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>8:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >= 8:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m = []
                    Y_m = []

        return X_f, Y_f
      
    def _regle_5(self):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(1, len(self._Y)):
            if self._Y[i] > self._Y[i-1]:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>6:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=6:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
            
            if self._Y[i] < self._Y[i-1]:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>6:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >= 6:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m = []
                    Y_m = []

        return X_f, Y_f
      
    def _regle_6(self):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(len(self._Y)):
            if self._Y[i] > self._moy:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>15:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=15:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
            
            if self._Y[i] < self._moy:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>15:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >= 15:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m = []
                    Y_m = []

        return X_f, Y_f
              
    def _regle_7(self):
        X_f = []
        Y_f = []
        X_p = [self._Y[0], self._Y[1]]
        Y_p = [self._Y[0], self._Y[1]]
        sign = np.sign(self._Y[1]-self._Y[0])
        for i in range(2,len(self._Y)):
            if np.sign(self._Y[i]-self._Y[i-1]) != sign:
                sign = np.sign(self._Y[i]-self._Y[i-1])
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>14:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=14:
                    X_f += X_p
                    Y_f += Y_p
            else:
                sign = np.sign(self._Y[i]-self._Y[i-1])
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f
    
    def _regle_8(self, LSL, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL or self._Y[i] < LSL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>8:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=8:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f

class fn_mr:
    def __init__(self, fn, X:list, Y:list, moy:float, USL:float,
                 title:str="Result"):
        
        self._col_3_sigma = "#880015"
        self._col_2_sigma = "#ED1C24"
        self._col_1_sigma = "#FF7F27"

        self._X = X
        self._Y = Y
        self._moy = moy
        self._USL = USL
        self._fn = tk.Toplevel(fn)
        self._fn.resizable(width=False, height=False)
        self._var_regle = tk.StringVar()
        self._fn.title(title)
        self._creation_fn()
        self._plot_configure()

    def _creation_fn(self):
        label = tk.LabelFrame(self._fn, text="Rules : ")
        label.grid(row=0, column=0)
        L_text = [" ; Large shift analysis: 1 or more points     \nmore than 3σ from the mean                  ",
                  " ; Large shift analysis: 2 of 3 consecutive   \npoints between 2σ and 3σ from the mean      ",
                  " ; Smaller shift and trends analysis:         \n4 of 5 consecutive points between 1σ and 3σ \nfrom the mean",
                  " ; Smaller shift analysis: 8 consecutive      \npoints on one side of the mean              ",
                  " ; Trends analysis: 6 consecutive points      \nsteadily increasing or decreasing           ",
                  " ; Stratification analysis: 15 consecutive    \npoints both above and below central line    ",
                  " ; Systematic variation analysis: 14          \nconsecutive points alternating up and down  ",
                  " ; Mixture analysis: 8 points in a row on     \nboth sides of the centre line upper than 1σ "]

        for i in range(8):
            r = tk.Radiobutton(label, text="Rule "+str(i+1) + L_text[i], value=i, variable=self._var_regle)
            r.grid(row=i, column=0, sticky="W")

        self._var_regle.set(0)

        bout = tk.Button(label, text="View", command=self._visualiser_resultat)
        bout.grid(row=8, column=0, sticky="NEWS")

        label = tk.Frame(self._fn)
        label.grid(row=0, column=1) 
        self._fig = Figure(figsize=(4,4)) 
        self._plot = self._fig.add_subplot(111)
        self._plot.plot(self._X, self._Y, "--xk")
        L = [np.min(self._X), np.max(self._X)]
        self._plot.plot(L, [self._USL, self._USL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*2/3, 
                            self._moy+(self._USL-self._moy)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*1/3, 
                            self._moy+(self._USL-self._moy)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._moy, self._moy], "-k")
        
        #self._plot.set_axis_off()     
        self._fig.subplots_adjust(left=0.2)
        self._canvas = FigureCanvasTkAgg(self._fig, master = label)   
        self._canvas.draw()
        label_2 = tk.Frame(label)
        label_2.grid(row=2, column=0, sticky='W') 
        NavigationToolbar2Tk(self._canvas, label_2).update()

        self._canvas.get_tk_widget().grid(row=1, column=0)

    def _plot_configure(self):
        label = tk.LabelFrame(self._fn, text="Graph parameters: ")
        label.grid(row=0, column=2)

        texte = tk.Label(label, text = 'Title:')
        texte.grid(row=0, column=0, sticky="E")
        self._entree_title = tk.Entry(label, width=15)
        self._entree_title.insert(0, "")
        self._entree_title.grid(row=0, column=1, sticky="E")
        self._entree_title.bind("<Key>", self._afficher_plot_event)
        self._entree_title.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_title.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'x label:')
        texte.grid(row=1, column=0, sticky="E")
        self._entree_xlabel = tk.Entry(label, width=15)
        self._entree_xlabel.insert(0, "")
        self._entree_xlabel.grid(row=1, column=1, sticky="E")
        self._entree_xlabel.bind("<Key>", self._afficher_plot_event)
        self._entree_xlabel.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_xlabel.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'y label:')
        texte.grid(row=2, column=0, sticky="E")
        self._entree_ylabel = tk.Entry(label, width=15)
        self._entree_ylabel.insert(0, "")
        self._entree_ylabel.grid(row=2, column=1, sticky="E")
        self._entree_ylabel.bind("<Key>", self._afficher_plot_event)
        self._entree_ylabel.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_ylabel.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Minimal x limit:')
        texte.grid(row=3, column=0, sticky="E")
        self._entree_lim_min_x = tk.Entry(label, width=8)
        self._entree_lim_min_x.insert(0, str(round(self._fig.gca().get_xlim()[0], 3)))
        self._entree_lim_min_x.grid(row=3, column=1, sticky="E")
        self._entree_lim_min_x.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_min_x.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_min_x.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Maximal x limit:')
        texte.grid(row=4, column=0, sticky="E")
        self._entree_lim_max_x = tk.Entry(label, width=8)
        self._entree_lim_max_x.insert(0, str(round(self._fig.gca().get_xlim()[1], 3)))
        self._entree_lim_max_x.grid(row=4, column=1, sticky="E")
        self._entree_lim_max_x.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_max_x.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_max_x.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Minimal y limit:')
        texte.grid(row=5, column=0, sticky="E")
        self._entree_lim_min_y = tk.Entry(label, width=8)
        self._entree_lim_min_y.insert(0, str(round(self._fig.gca().get_ylim()[0], 3)))
        self._entree_lim_min_y.grid(row=5, column=1, sticky="E")
        self._entree_lim_min_y.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_min_y.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_min_y.bind("<Leave>", self._afficher_plot_event)

        texte = tk.Label(label, text = 'Maximal y limit:')
        texte.grid(row=6, column=0, sticky="E")
        self._entree_lim_max_y = tk.Entry(label, width=8)
        self._entree_lim_max_y.insert(0, str(round(self._fig.gca().get_ylim()[1], 3)))
        self._entree_lim_max_y.grid(row=6, column=1, sticky="E")
        self._entree_lim_max_y.bind("<Key>", self._afficher_plot_event)
        self._entree_lim_max_y.bind("<FocusOut>", self._afficher_plot_event)
        self._entree_lim_max_y.bind("<Leave>", self._afficher_plot_event)

        self._bout_3s = tk.Button(label, text = 'Color of 3σ limit:', 
                                  command=self._couleur_3_limites)
        self._bout_3s.configure(bg=self._col_3_sigma)
        self._bout_3s.grid(row=7, column=0, columnspan=2, sticky="WESN")

        self._bout_2s = tk.Button(label, text = 'Color of 2σ limit:', 
                                  command=self._couleur_2_limites)
        self._bout_2s.configure(bg=self._col_2_sigma)
        self._bout_2s.grid(row=8, column=0, columnspan=2, sticky="WESN")

        self._bout_1s = tk.Button(label, text = 'Color of 1σ limit:', 
                                  command=self._couleur_1_limites)
        self._bout_1s.configure(bg=self._col_1_sigma)
        self._bout_1s.grid(row=9, column=0, columnspan=2, sticky="WESN")

    def _afficher_plot_event(self, event):
        self._visualiser_resultat()

    def _couleur_3_limites(self):
        self._col_3_sigma = askcolor(title="Color of 3σ limit")[1]
        self._bout_3s.configure(bg=self._col_3_sigma)
        self._visualiser_resultat()

    def _couleur_2_limites(self):
        self._col_2_sigma = askcolor(title="Color of 2σ limit")[1]
        self._bout_2s.configure(bg=self._col_2_sigma)
        self._visualiser_resultat()

    def _couleur_1_limites(self):
        self._col_1_sigma = askcolor(title="Color of 1σ limit")[1]
        self._bout_1s.configure(bg=self._col_1_sigma)
        self._visualiser_resultat()

    def _visualiser_resultat(self):
        try:
            self._afficher_plot()

            if int(self._var_regle.get())==0:
                X, Y = self._regle_1(self._USL)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==1:
                X, Y = self._regle_2(self._moy+(self._USL-self._moy)*2/3)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==2:
                X, Y = self._regle_3(self._moy+(self._USL-self._moy)/3)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==3:
                X, Y = self._regle_4(self._moy)
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==4:
                X, Y = self._regle_5()
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==5:
                X, Y = self._regle_6()
                self._plot.plot(X, Y, "or")
            elif int(self._var_regle.get())==6:
                X, Y = self._regle_7()
                self._plot.plot(X, Y, "or")
            else:
                X, Y = self._regle_8(self._moy+(self._USL-self._moy)/3)
                self._plot.plot(X, Y, "or")

            self._canvas.draw()
            self._fn.update_idletasks()
        except:
            showwarning("Problem", "Drawing")

    def _afficher_plot(self):
        self._plot.cla()

        self._plot.plot(self._X, self._Y, "--xk")
        L = [np.min(self._X), np.max(self._X)]
        self._plot.plot(L, [self._USL, self._USL], "-", color=self._col_3_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*2/3, 
                            self._moy+(self._USL-self._moy)*2/3], "-", color=self._col_2_sigma)
        self._plot.plot(L, [self._moy+(self._USL-self._moy)*1/3, 
                            self._moy+(self._USL-self._moy)*1/3], "-", color=self._col_1_sigma)
        self._plot.plot(L, [self._moy, self._moy], "-k")

        self._plot.set_ylim([float(self._entree_lim_min_y.get()), 
                             float(self._entree_lim_max_y.get())])

        self._plot.set_xlim([float(self._entree_lim_min_x.get()), 
                             float(self._entree_lim_max_x.get())])
        
        self._plot.set_xlabel(self._entree_xlabel.get())
        self._plot.set_ylabel(self._entree_ylabel.get())
        self._plot.set_title(self._entree_title.get())
        self._canvas.draw()
        self._fn.update_idletasks()

    def _regle_1(self, USL):
        X_f = []
        Y_f = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_f.append(self._X[i])
                Y_f.append(self._Y[i])
        return X_f, Y_f

    def _regle_2(self, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>2:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=2:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p.pop(0)
                    Y_p.pop(0)
            
        return X_f, Y_f

    def _regle_3(self, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>4:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=4:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f
    
    def _regle_4(self, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>8:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=8:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
        
        return X_f, Y_f
      
    def _regle_5(self):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        X_m = []
        Y_m = []
        for i in range(1, len(self._Y)):
            if self._Y[i] > self._Y[i-1]:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>6:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=6:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []
            
            if self._Y[i] < self._Y[i-1]:
                X_m.append(self._X[i])
                Y_m.append(self._Y[i])
                if len(X_m)>6:
                    X_m.pop(0)
                    Y_m.pop(0)
                if len(X_m) >= 6:
                    X_f += X_m
                    Y_f += Y_m
            else:
                if len(X_m)>0:
                    X_m = []
                    Y_m = []

        return X_f, Y_f
      
    def _regle_6(self):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > self._moy:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>15:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=15:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f
              
    def _regle_7(self):
        X_f = []
        Y_f = []
        X_p = [self._Y[0], self._Y[1]]
        Y_p = [self._Y[0], self._Y[1]]
        sign = np.sign(self._Y[1]-self._Y[0])
        for i in range(2,len(self._Y)):
            if np.sign(self._Y[i]-self._Y[i-1]) != sign:
                sign = np.sign(self._Y[i]-self._Y[i-1])
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>14:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=14:
                    X_f += X_p
                    Y_f += Y_p
            else:
                sign = np.sign(self._Y[i]-self._Y[i-1])
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f
    
    def _regle_8(self, USL):
        X_f = []
        Y_f = []
        X_p = []
        Y_p = []
        for i in range(len(self._Y)):
            if self._Y[i] > USL:
                X_p.append(self._X[i])
                Y_p.append(self._Y[i])
                if len(X_p)>8:
                    X_p.pop(0)
                    Y_p.pop(0)
                if len(X_p) >=8:
                    X_f += X_p
                    Y_f += Y_p
            else:
                if len(X_p)>0:
                    X_p = []
                    Y_p = []

        return X_f, Y_f

class class_fn:
    def __init__(self):
        # Variables
        self._L_donnee = []
        self._L_limites = []
        self._L_constantes = []
        self._fn = tk.Tk()

        # Variable
        self._L_var_col_cal = []
        self._var_col = tk.IntVar(self._fn, value = 1)
        self._var_lign = tk.IntVar(self._fn, value = 10)
        self._var_chart = tk.StringVar(self._fn)
        self._var_chart_limit = tk.StringVar(self._fn)
        self._var_sigma = tk.StringVar(self._fn)
        self._var_mu = tk.StringVar(self._fn)

        self._var_nb_it = tk.IntVar(self._fn, value=1000_000)

        self._police =  Font(family = "Time", size = 9)
        self._police_g =  Font(family = "Time", size = 13)
        self._fn.title('Control chart')

        self._fn.rowconfigure(0, weight=0)
        self._fn.rowconfigure(1, weight=1)
        self._fn.rowconfigure(2, weight=0)
        self._fn.columnconfigure(0, weight=1)

        label_donnees = tk.LabelFrame(self._fn, text="Add data:")
        label_donnees.grid(row=0, column=0, sticky="EW")
        label_donnees.rowconfigure(0, weight=1)
        label_donnees.columnconfigure(0, weight=1)
        label_donnees.columnconfigure(1, weight=1)
        self._parametre(label_donnees)

        label_donnees = tk.LabelFrame(self._fn, text="Data:")
        label_donnees.grid(row=1, column=0, sticky="SNWE")
        label_donnees.columnconfigure(0, weight=1)
        label_donnees.columnconfigure(1, weight=1)
        self._xy_scroll_label(label_donnees)

        label_donnees = tk.LabelFrame(self._fn, text="Calcul:")
        label_donnees.grid(row=2, column=0, sticky="NEWS")
        label_donnees.rowconfigure(0, weight=1)
        label_donnees.rowconfigure(1, weight=1)
        label_donnees.columnconfigure(0, weight=1)
        label_donnees.columnconfigure(1, weight=1)
        self._calcul(label_donnees)

        self._fn.mainloop()

    def _xy_scroll_label(self, frame, lign:int=0, col:int=0):
        vscrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vscrollbar.grid(row=lign, column=col+1, sticky='ns')

        hscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hscrollbar.grid(row=lign+1, column=col, sticky='we')

        self._canvas = tk.Canvas(frame, width=500, height=200,
                           yscrollcommand=vscrollbar.set,
                           xscrollcommand=hscrollbar.set)
        self._canvas.grid(row=lign, column=col, sticky="NEWS")

        vscrollbar.config(command=self._canvas.yview)
        hscrollbar.config(command=self._canvas.xview)

        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

        self._frame = tk.Frame(self._canvas)
        self._canvas.create_window((0, 0), window=self._frame,
                                           anchor=tk.NW)

    def _parametre(self, frame, lign:int=0, col:int=0):
        cdr = tk.Frame(frame)
        cdr.grid(row=lign, column = col, sticky="WE")
        cdr.rowconfigure(0, weight=1)
        cdr.columnconfigure(0, weight=0)
        cdr.columnconfigure(1, weight=1)
        cdr.columnconfigure(2, weight=0)
        cdr.columnconfigure(3, weight=1)
        cdr.columnconfigure(4, weight=1)

        lb = tk.Label(cdr, text = "Number of lines: ")
        lb.grid(row=0, column=0 )
        sp = tk.Spinbox(cdr, from_=1, to=99, width=2,
                         textvariable = self._var_lign)
        sp.grid(row=0, column=1, sticky="W")

        lb = tk.Label(cdr, text = "Number of columns: ")
        lb.grid(row=0, column=2) 

        sp = tk.Spinbox(cdr, from_=1, to=99, width=2,
                         textvariable = self._var_col)
        sp.grid(row=0, column=3, sticky="W")

        bout = tk.Button(cdr, text="Draw",
                          command=self._afficher_tab)
        bout.grid(row=0, column=4, sticky="NEWS", rowspan=2)

        bout = tk.Button(frame, text="Open",
                          command=self._command_ouvrir)
        bout.grid(row=lign, column=col+1, sticky="NEWS")

    def _afficher_tab(self):
        try :
            for child in self._frame.winfo_children():
                child.destroy()
            
            for child in self._label_Frame_col.winfo_children():
                child.destroy()
            
            if int(self._var_col.get()) <= 0 :
                self._var_col.set(1)
            if int(self._var_lign.get()) <= 0 :
                self._var_lign.set(1)

            for j in range(int(self._var_col.get())):
                    cdr = tk.Label(self._frame, text="Column "+str(j+1), borderwidth=1, 
                                   relief=tk.RIDGE)
                    cdr.grid(row = 0, column=1+j, sticky="nesw")
            
            cdr = tk.Label(self._frame, text="Index",
                           borderwidth=1, relief=tk.RIDGE)
            cdr.grid(row = 0, column=0, rowspan=3, sticky="nesw")

            for i in range(int(self._var_lign.get())):
                cdr = tk.Label(self._frame, text=str(i+1),
                               borderwidth=1, relief=tk.RIDGE)
                cdr.grid(row = 3+i, column=0, sticky="nesw")
            
            del self._L_donnee
            self._L_donnee = []
            self._L_var_col_cal = []
            for i in range(int(self._var_col.get())):
                var_val = tk.IntVar(self._fn, value=0)
                r = tk.Checkbutton(self._label_Frame_col, text=str(i+1), variable=var_val, 
                                   onvalue= 1, offvalue=0)
                r.grid(row=0, column=i, sticky="NEWS")
                self._L_var_col_cal.append(var_val)

                X = []
                for j in range(int(self._var_lign.get())):
                    en = tk.Entry(self._frame, width = 10, bg="#F0F0ED", relief=tk.RIDGE)
                    en.insert(0, 0)
                    en.grid(row=j+3, column=i+1,
                            sticky="nesw")
                    X.append(en)
                self._L_donnee.append(X)

            self._frame.update_idletasks()
            self._canvas.config(scrollregion=self._canvas.bbox("all"))
        except:
            showerror(title="Problem", message="Scale issue")

    def _command_ouvrir(self):
        try:
            lien = askopenfilename(title="Open excel", initialdir=path.expanduser("~/Documents"),
                                filetypes = [("Excel files", ".xlsx")])
            tab = pd.read_excel(lien, index_col=None)
            tab = tab.to_numpy().T
            self._L_donnee = []
            
            for child in self._frame.winfo_children():
                child.destroy()
            
            for child in self._label_Frame_col.winfo_children():
                child.destroy()

            for j in range(tab.shape[0]):
                    cdr = tk.Label(self._frame, text="Column "+str(j+1), borderwidth=1, 
                                   relief=tk.RIDGE)
                    cdr.grid(row = 0, column=1+j, sticky="nesw")
            
            cdr = tk.Label(self._frame, text="Index",
                           borderwidth=1, relief=tk.RIDGE)
            cdr.grid(row = 0, column=0, rowspan=3, sticky="nesw")

            for i in range(tab.shape[1]):
                cdr = tk.Label(self._frame, text=str(i+1),
                               borderwidth=1, relief=tk.RIDGE)
                cdr.grid(row = 3+i, column=0, sticky="nesw")
            
            del self._L_donnee
            self._L_donnee = []
            self._L_var_col_cal = []
            self._var_col.set(tab.shape[0])
            for i in range(int(self._var_col.get())):
                var_val = tk.IntVar(self._fn, value=0)
                r = tk.Checkbutton(self._label_Frame_col, text=str(i+1), variable=var_val, 
                                   onvalue= 1, offvalue=0)
                r.grid(row=0, column=i, sticky="NEWS")
                self._L_var_col_cal.append(var_val)

                X = []
                for j in range(tab.shape[1]):
                    en = tk.Entry(self._frame, width = 10, bg="#F0F0ED", relief=tk.RIDGE)
                    if str(tab[i,j])=="nan":
                        en.insert(0, "")
                    else:
                        en.insert(0, tab[i, j])
                    en.grid(row=j+3, column=i+1,
                            sticky="nesw")
                    X.append(en)
                self._L_donnee.append(X)

            self._frame.update_idletasks()
            self._canvas.config(scrollregion=self._canvas.bbox("all"))
            
        except:
            showerror(title="Problem", message="Opening problem")

    def _calcul(self, frame, lign:int=0, col:int=0):
        self._label_Frame_col = tk.LabelFrame(frame, text="Select column:")
        self._label_Frame_col.grid(row=lign, column=col, sticky="NEWS")

        Frame = tk.LabelFrame(frame, text="Select chart:")
        Frame.grid(row=lign+1, column=col, sticky="NEWS")

        r = tk.Radiobutton(Frame, text='X Chart', value=0, variable=self._var_chart)
        r.grid(row=0, column=0, sticky="NEWS")

        r = tk.Radiobutton(Frame, text='R Chart', value=1, variable=self._var_chart)
        r.grid(row=0, column=1, sticky="NEWS")

        r = tk.Radiobutton(Frame, text='s Chart', value=2, variable=self._var_chart)
        r.grid(row=0, column=2, sticky="NEWS")

        self._var_chart.set(0)

        Frame = tk.LabelFrame(frame, text="Select the method for calculating limits:")
        Frame.grid(row=lign+2, column=col, sticky="NEWS")

        lab = tk.Label(Frame, text="µ")
        lab.grid(row=0, column=0, sticky="E")

        lab = tk.Entry(Frame, width=12,
                         textvariable = self._var_mu)
        lab.grid(row=0, column=1, sticky="E")

        lab = tk.Label(Frame, text="σ")
        lab.grid(row=0, column=2, sticky="E")

        lab = tk.Entry(Frame, width=12,
                         textvariable = self._var_sigma)
        lab.grid(row=0, column=3, sticky="E")

        r = tk.Radiobutton(Frame, text='Known σ', value=0, variable=self._var_chart_limit)
        r.grid(row=0, column=4, sticky="NEWS")

        r = tk.Radiobutton(Frame, text='Estimate s', value=1, variable=self._var_chart_limit)
        r.grid(row=0, column=5, sticky="NEWS")

        r = tk.Radiobutton(Frame, text='Unknown s', value=2, variable=self._var_chart_limit)
        r.grid(row=0, column=6, sticky="NEWS")

        self._var_chart_limit.set(0)

        Frame = tk.LabelFrame(frame, text="Calculating limits:")
        Frame.grid(row=lign+3, column=col, sticky="NEWS")

        Frame.columnconfigure(0, weight=0)
        Frame.columnconfigure(1, weight=0)
        Frame.columnconfigure(2, weight=1)
        Frame.columnconfigure(3, weight=1)

        lab = tk.Label(Frame, text="Iteration")
        lab.grid(row=0, column=0, sticky="E")

        lab = tk.Entry(Frame, width=12,
                         textvariable = self._var_nb_it)
        lab.grid(row=0, column=1, sticky="E")

        bout = tk.Button(Frame, text="Calculating limits",
                          command=self._command_calcul_limit)
        bout.grid(row=0, column=2, sticky="NEWS")

        self._progressbar = Progressbar(Frame, orient= tk.HORIZONTAL, 
                                           length=100, mode='determinate')
        self._progressbar.grid(row=0, column=3, sticky="NEWS")

        bout = tk.Button(frame, text="Visualize",
                          command=self._command_calcul)
        bout.grid(row=lign, column=col+1, sticky="NEWS", rowspan=4)

    def _command_calcul_limit(self):
        nb_val = 500_000
        nb_it = self._var_nb_it.get()//nb_val
        nb_it = 1 if nb_it < 1 else nb_it
        d2, d3, c4 = 0, 0, 0
        for i in range(nb_it):
            self._progressbar['value'] = 100*i/nb_it
            self._fn.update_idletasks()
            nb = np.sum([elmt.get() for elmt in self._L_var_col_cal])
            if nb <= 2:
                nb = 2
            L = d2_d3_c4(nb_val, nb)
            d2 += L[0]
            d3 += L[1] 
            c4 += L[2]
        d2 = d2/nb_it 
        d3 = d3/nb_it
        c4 = c4/nb_it
        self._L_limites = A_E(d2, d3, c4, nb)

        self._progressbar['value'] = 0
        self._fn.update_idletasks()
        try:
            n = len(self._L_donnee)
            if n > 0:
                p = len(self._L_donnee[0])
                if p > 0 :
                    tab = []
                    for i in range(n):
                        L = []
                        if self._L_var_col_cal[i].get() > 0:
                            for j in range(p):
                                try:
                                    L.append(float(self._L_donnee[i][j].get()))
                                except:
                                    pass
                            tab.append(L)
                    tab = np.array(tab)

                    L_X = [np.mean(tab[:, i]) for i in range(tab.shape[1])]
                    L_R = [np.max(tab[:, i])-np.min(tab[:, i]) for i in range(tab.shape[1])]
                    L_s = [np.std(tab[:, i], ddof=1) for i in range(tab.shape[1])]
                    self._L_constantes = [np.mean(L_X), np.mean(L_R), np.mean(L_s)]
        except:
            showerror(title="Problem", message="Data problem")

    def _command_calcul(self):
        try:
            if len(self._L_limites) == 0 or len(self._L_constantes)==0:
                showerror(title="Problem", message="Calculate control limits")
            else:
                n = len(self._L_donnee)
                if n > 0:
                    p = len(self._L_donnee[0])
                    if p > 0 :
                        if np.sum([elmt.get() for elmt in self._L_var_col_cal]) >= 2:
                            tab = []
                            for i in range(n):
                                L = []
                                if self._L_var_col_cal[i].get() > 0:
                                    for j in range(p):
                                        try:
                                            L.append(float(self._L_donnee[i][j].get()))
                                        except:
                                            pass
                                    tab.append(L)
                            tab = np.array(tab)

                            L_X = [np.mean(tab[:, i]) for i in range(tab.shape[1])]
                            L_s = [np.std(tab[:, i], ddof=1) for i in range(tab.shape[1])]

                            if int(self._var_chart.get()) == 0:
                                self._X_chart(L_X, tab.shape[0])
                            elif int(self._var_chart.get()) == 1:
                                self._R_chart(L_X)
                            else:
                                self._s_chart(L_s)

                        else:
                            showerror(title="Problem", message="Select one column")

        except:
            showerror(title="Problem", message="Data problem")

    def _X_chart(self, L, k):
        if int(self._var_chart_limit.get()) == 0:
            #sigma fixed
            sigma = float(self._var_sigma.get())
            mu = float(self._var_mu.get())
            LSL = mu - 3*sigma/sqrt(k)
            USL = mu + 3*sigma/sqrt(k)
            fn(self._fn, [i+1 for i in range(len(L))], L, mu, LSL, USL,
                    "x chart")
        elif int(self._var_chart_limit.get()) == 1:
            # self._L_constantes = X, R, s
            # self._L_limites = [A2, A3, B3, B4, B5, B6, D1, D2, D3, D4]
            LSL = self._L_constantes[0] - self._L_limites[1]*self._L_constantes[2]
            USL = self._L_constantes[0] + self._L_limites[1]*self._L_constantes[2]
            mu = self._L_constantes[0]

            fn(self._fn, [i+1 for i in range(len(L))], L, mu, LSL, USL,
                    "x chart")
        else :
            # self._L_constantes = X, R, s
            # self._L_limites = [A2, A3, B3, B4, B5, B6, D1, D2, D3, D4]
            LSL = self._L_constantes[0] - self._L_limites[0]*self._L_constantes[1]
            USL = self._L_constantes[0] + self._L_limites[0]*self._L_constantes[1]
            mu = self._L_constantes[0]
            fn(self._fn, [i+1 for i in range(len(L))], L, mu, LSL, USL,
                    "x chart")

    def _R_chart(self, L):
        L_mr = []
        for i in range(1, len(L)):
            L_mr.append(abs(L[i]-L[i-1]))
        if int(self._var_chart_limit.get()) == 0:
            # self._L_constantes = X, R, s
            # self._L_limites = [A2, A3, B3, B4, B5, B6, D1, D2, D3, D4]
            LSL = self._L_limites[len(self._L_limites)-4]*self._L_constantes[1]
            USL = self._L_limites[len(self._L_limites)-3]*self._L_constantes[1]
            fn_mr(self._fn, [i+2 for i in range(len(L_mr))], L_mr, LSL, USL,
                    "R chart")
        else :
            # self._L_constantes = X, R, s
            # self._L_limites = [A2, A3, B3, B4, B5, B6, D1, D2, D3, D4]
            LSL = self._L_limites[len(self._L_limites)-2]*self._L_constantes[1]
            USL = self._L_limites[len(self._L_limites)-1]*self._L_constantes[1]
            fn_mr(self._fn, [i+2 for i in range(len(L_mr))], L_mr, LSL, USL,
                    "R chart")

    def _s_chart(self, L):
        if int(self._var_chart_limit.get()) == 0:
            #sigma fixed
            sigma = float(self._var_sigma.get())
            LSL = sigma*self._L_limites[4]
            USL = sigma*self._L_limites[5]
            fn(self._fn, [i+1 for i in range(len(L))], L, sigma, LSL, USL,
                    "s chart")
        else :
            # self._L_constantes = X, R, s
            # self._L_limites = [A2 0, A3 1, B3 2, B4 3, B5 4, B6 5, 
            #  D1, D2, D3, D4]
            LSL = self._L_limites[4]*self._L_constantes[2]
            USL = self._L_limites[5]*self._L_constantes[2]
            mu = self._L_constantes[2]
            fn(self._fn, [i+1 for i in range(len(L))], L, mu, LSL, USL,
                    "s chart")

if '__main__' == __name__:
    fn = class_fn()
    