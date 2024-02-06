# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 15:12:36 2021

@author: lakle
"""
#%% NOtes
#Pause


#import sys
#sys.modules[__name__].__dict__.clear()
##------------------------------------------------------------
import tkinter as tk
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import serial

#plt.close('all')

#%% Inputs
arduino_port=('COM6')
baud=9600

#%% Definitions
def center_window(width=300, height=3000):
    screen_width = float(root1.winfo_screenwidth())
    screen_height =float(root1.winfo_screenheight())
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root1.geometry('%dx%d+%d+%d' % (width, height, x, y-35))

def data_read():
    ser.flushInput()
    data = ser.readline()
    data = ser.readline()
    data=data[:-2].split('\t')
    data=np.array(data).astype(float)
    return data

def save_data_to_file(now,kk,zeitachse,fileName,Druck,Feuchte,Temperatur):
    global zeitachse_old, LaserID
    stoptimer=now+timedelta(hours=0,minutes=0,seconds=Dauer)
    dt_stop=stoptimer.strftime("%d/%m/%Y %H:%M:%S")

    if kk==0:
        file=open(fileName,'w')
        file.write('Start:'+dt_string+'\n')
        file.write('Stop:'+dt_stop+'\n')
        file.write('LaserID:'+LaserID+'\n')
        file.write('Time (minutes)\tPressure (mbar)\tHumdity(%)\tTemperature (°C)\n')
        for pp in range(len(zeitachse)):
            file.write(str(round(zeitachse[pp],2))+"\t"+str(Druck[pp])+"\t"+str(Feuchte[pp])+"\t"+str(Temperatur[pp])+"\n")
        file.close()
        zeitachse_old=len(zeitachse)
    else:
        file=open(fileName,'a')
        for pp in range(zeitachse_old,len(zeitachse)):
            file.write(str(round(zeitachse[pp],2))+"\t"+str(Druck[pp])+"\t"+str(Feuchte[pp])+"\t"+str(Temperatur[pp])+"\n")
        file.close()
        zeitachse_old=len(zeitachse)

def continue_now():
    global continuePlotting
    continuePlotting=True

def pause_now():
    global continuePlotting
    continuePlotting=False

def soll_uebergabe1():
     send=str(pressureEntry1.get().replace(",","."))
     send=str(float(send)*100)
     ser.write(send)
     #print(send)
     #ser.flushInput()

#def save_ani():
#    plt.savefig('Measurement_'+datetime.now().strftime('%d.%m.%Y_%H''%M''%S')+'.png')
#         #ani.save('ani.mp4',fps=2)

def app():
    # initialise a window.
    global Dauer, Interval, LaserID, Plotinterval, Saveinterval, soll_Pressure
    Interval=float(spin.get().replace(',','.'))
    Dauer=int(entrysimutime.get().replace(',','.'))*60
    LaserID=str(entry_laserID.get())
    Plotinterval=float(entry_plotinterval.get().replace(",","."))
    Saveinterval=float(entry_saveinterval.get().replace(",","."))
    soll_Pressure=str(pressureEntry1.get().replace(",","."))
    soll_uebergabe1()

    def soll_uebergabe():
         send=str(pressureEntry.get().replace(",","."))
         send=str(float(send)*100)
         ser.write(send)
         #print(send)
         ser.flushInput()

    def Meas_Stop():
        global continuePlotting, Meas_Cont
        continuePlotting = False
        Meas_Cont=False
        ser.close()
        root.destroy()

    root = tk.Tk()
    root.config(background='white')
    root.geometry("1000x700")
    root.title('Klimakammer DPSSL V0.1')

    stoptimer=now+timedelta(hours=0,minutes=0,seconds=Dauer)
    dt_stop=stoptimer.strftime("%d/%m/%Y %H:%M:%S")
    tk.Label(root, text="LaserID: "+str(LaserID), bg='white').pack(anchor="e",padx=100)
    tk.Label(root, text="Startzeit: "+dt_string, bg='white').pack(anchor="e",padx=100)
    tk.Label(root, text="Endzeit: "+str(dt_stop), bg='white').pack(anchor="e",padx=100)

    entry_Laufzeit=tk.Entry(root, bg='white')
    entry_Laufzeit.pack(anchor="e", padx=100, pady=5)

    ueberschrift = tk.Label(root, fg="black",text='Druck  Temperatur  Feuchtigkeit')
    ueberschrift.place(relx=0.45,rely=0)
    liveshow=tk.Entry(root, bg='white')
    liveshow.place(relx=0.45,rely=0.04,width=180)
    liveshow.delete(0,tk.END)

    pressuretitle=tk.Label(root, fg="blue",text="Gewünschter Druck (mbar)" )
    pressuretitle.place(x=360,y=65,width=150)
    pressureEntry=tk.Entry(root, bg='white')
    pressureEntry.place(x=510,y=65,width=80)
    pressureEntry.delete(0,tk.END)
    pressureEntry.insert(0,soll_Pressure)
    press_button = tk.Button(root,text='Send',width=5,command=soll_uebergabe)
    press_button.place(x=590,y=65,height=20)

    pausebutton=tk.Button(root,text='Pause',width=20,command=pause_now)
    pausebutton.place(x=50,y=15)

    continuebutton=tk.Button(root,text='Continue',bg='yellow',width=20,command=continue_now)
    continuebutton.place(x=50,y=65)

    button = tk.Button(root, text='Stop', width=20, bg='red',command=Meas_Stop)
    button.place(x=50,y=90)

    fig = Figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    graph = FigureCanvasTkAgg(fig, master=root)
    #graph.get_tk_widget().pack(fill='both',expand=True)
    graph.get_tk_widget().place(relx=0,rely=0.2,relheight=0.8,relwidth=1)

    def plotter():
        global continuePlotting, Dauer, Interval, Plotinterval, Saveinterval, plottime_save, savetime, Meas_Cont, soll_Pressure

        plottime_save=[]
        savetime=[]
        starttime_plot=time.time()
        starttime_data=time.time()
        starttime_dauer=time.time()
        starttime_save=time.time()
        Druck=[]
        Feuchte=[]
        Temperatur=[]
        zeitachse=[]
        ii=0
        jj=0
        kk=0
        h=0

        while Meas_Cont:
            while continuePlotting:
                current_time=time.time()
                diff_plot=current_time-starttime_plot
                diff_data=current_time-starttime_data
                diff_dauer=current_time-starttime_dauer
                diff_save=current_time-starttime_save

                if diff_data>Interval:
                    doit=True
                    #h=0
                    while doit:
                        try:
                            zwischenspeicher=data_read()
                            #print(zwischenspeicher)
                            Druck.append(zwischenspeicher[0]/100)
                            Feuchte.append(zwischenspeicher[1])
                            Temperatur.append(zwischenspeicher[2])
                            zeitachse.append((current_time-starttime_dauer)/60)

                            entry_Laufzeit.delete(0,tk.END)
                            liveshow.delete(0,tk.END)
                            entry_Laufzeit.insert(0,str(timedelta(seconds=int(current_time-starttime_dauer))))
                            liveshow.insert(0,str(round(Druck[jj],2))+' (mbar)   '+str(Temperatur[jj])+'°C   '+str(Feuchte[jj])+'%')

                            doit=False

                            #if zwischenspeicher[0]<10:
                            #    doit=True

                            #if Temperatur[jj]>(1.5*Temperatur[jj-1]) or Temperatur[jj]<(0.5*Temperatur[jj-1]):
                            #     print('Error temperature measuring, try measuring again')
                            #     doit=True

                        except:
                            doit=True
                            if h<=20:
                                h+=1
                                print("Got Error, try measuring again")
                            else:
                                continuePlotting=False
                                doit=False
                                save_data_to_file(now,kk,zeitachse,fileName,Druck,Feuchte,Temperatur)

                    starttime_data=jj*Interval+starttime_dauer
                    jj+=1

                if diff_plot>Plotinterval:
                    ax1.cla()
                    ax2.cla()
                    ax3.cla()
                    ax1.grid()

                    ax1.set_ylabel("Druck (mbar)")
                    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
                    plt.setp(ax1.get_xticklabels(), visible=False)
                    ax2.grid()
                    ax2.set_ylabel("Temperatur"+"("+u"\N{DEGREE SIGN}"+"C)")
                    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                    plt.setp(ax2.get_xticklabels(), visible=False)
                    ax3.grid()
                    ax3.set_ylabel("Feuchtigkeit (%)")
                    ax3.set_xlabel("Time (min.)")
                    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

                    ax1.plot(zeitachse,Druck,'b',linewidth=0.5)
                    ax2.plot(zeitachse,Temperatur,color='orange',linewidth=0.5)
                    ax3.plot(zeitachse,Feuchte,'g',linewidth=0.5)

                    starttime_plot=ii*Plotinterval+starttime_dauer
                    ii+=1
                    graph.draw()

                if diff_save>Saveinterval:
                    #savefunction durchfuehren
                    save_data_to_file(now,kk,zeitachse,fileName,Druck,Feuchte,Temperatur)
                    kk+=1
                    starttime_save=kk*Saveinterval+starttime_dauer

                if diff_dauer>Dauer:
                    #savefunction durchfuehren
                    save_data_to_file(now,kk,zeitachse,fileName,Druck,Feuchte,Temperatur)
                    kk+=1
                    starttime_save=kk*Saveinterval+starttime_dauer
                    continuePlotting = False
                    Meas_Cont=False

        ser.close()

    threading.Thread(target=plotter).start()
    root.mainloop()

#%% First Window
root1 = tk.Tk()
root1.config(background='white')
root1.title('Property window')

label_laserID=tk.Label(root1,bg='grey',text='Laser ID:')
label_laserID.grid(row=0,column=0, padx=10, pady=5)
entry_laserID=tk.Entry(root1,bg='white')
entry_laserID.grid(row=0,column=1, padx=10, pady=5)
entry_laserID.delete(0,tk.END)
entry_laserID.insert(0,"FNr2352_PB6861_R2354_LD3456")

simutime=tk.Label(root1,bg='grey',text='Measurement time (min):')
simutime.grid(row=1,column=0, padx=10, pady=5)
entrysimutime=tk.Entry(root1,bg='white')
entrysimutime.grid(row=1,column=1, padx=10, pady=5)
entrysimutime.delete(0,tk.END)
entrysimutime.insert(0,str(10))

step=tk.Label(root1,bg='grey',text='Time Step (sec/>10ms):')
step.grid(row=2,column=0, padx=10, pady=5)
spin=tk.Entry(root1,bg='white')
spin.grid(row=2,column=1, padx=10, pady=5)
spin.delete(0,tk.END)
spin.insert(0,str(0.5))

label_plotinterval=tk.Label(root1,bg='grey',text='Plotinterval (sec):')
label_plotinterval.grid(row=3,column=0, padx=10, pady=5)
entry_plotinterval=tk.Entry(root1,bg='white')
entry_plotinterval.grid(row=3,column=1, padx=10, pady=5)
entry_plotinterval.delete(0,tk.END)
entry_plotinterval.insert(0,str(0.5))

label_saveinterval=tk.Label(root1,bg='grey',text='Saveinterval (sec):')
label_saveinterval.grid(row=4,column=0, padx=10, pady=5)
entry_saveinterval=tk.Entry(root1,bg='white')
entry_saveinterval.grid(row=4,column=1, padx=10, pady=5)
entry_saveinterval.delete(0,tk.END)
entry_saveinterval.insert(0,str(120))

pressuretitle=tk.Label(root1, fg="blue",text="Gewünschter Druck (mbar)" )
pressuretitle.grid(row=5,column=0, padx=10, pady=5)
pressureEntry1=tk.Entry(root1, bg='white')
pressureEntry1.grid(row=5,column=1, padx=10, pady=5)
pressureEntry1.delete(0,tk.END)
pressureEntry1.insert(0,str(1050))

#%% Serial Port Connection
try:
    ser=serial.Serial(arduino_port,baud)
except serial.SerialException :
    #print("Error while trying to read Arduino ")
    ser.close()
    ser=serial.Serial(arduino_port,baud)
#%%
Meas_Cont=True
continuePlotting = True

now = datetime.now()
dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
fileName=('Measurement_'+now.strftime('%d.%m.%Y_%H %M %S')+'.txt')

gobutton=tk.Button(root1,text='Starte den Graph',bg='blue',command=app)
gobutton.grid(row=6,column=1 ,padx=10, pady=5)

center_window(500,250)

root1.mainloop()
