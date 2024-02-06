# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 11:13:24 2023

@author: kilia
"""

 
import tkinter as tk
import serial as ser
import time
import serial.tools.list_ports
import numpy as np
import pandas as pd


 
#%% Serial Port Connection

# Open a serial port at 9600 baud rate
try:
    ser_port=ser.Serial('COM3', 9600)
except serial.SerialException :
    #print("Error while trying to read Arduino ")
    ser_port.close()
    ser_port=serial.Serial('COM3', 9600)
    

#Definitions
#%%
#inputs for the scan 

def steps():
    x_value = int(xEntry1.get())
    y_value = int(yEntry1.get())
    z_value = int(zEntry1.get())
    return x_value, y_value, z_value

#%% Encode the values to utf-8
 
def encoder(enc):
    encoded_command = enc.encode('utf-8')
    return encoded_command

#%% Homes the stage after moving in 1. direction

def homer(axis,value):
    x_string_neg = 'R1'+axis + '-'+ str(value)
    homing=encoder(x_string_neg)
    return homing

#%% Actions
  

#Write moving values to string
def xwriter():
    step=int(xcountEntry1.get())
    for i in range(step):
        x_string = 'R1X' + str(xEntry1.get().replace(",","."))
        ser_port.write(encoder(x_string))
        time.sleep(0.5)

    
def ywriter():
    step=int(ycountEntry1.get())
    for i in range(step):
        y_string = 'R1Y' + str(yEntry1.get().replace(",","."))
        ser_port.write(encoder(y_string))
        time.sleep(0.5)

    
def zwriter():
    step=int(zcountEntry1.get())
    for i in range(step):
        z_string = 'R1Z' + str(zEntry1.get().replace(",","."))
        ser_port.write(encoder(z_string))
        time.sleep(0.5)



#Scanning routine scans power values in a xyz-matrix in the dimension of the "No x/y/z-steps"
#given in the GUI-window 
def scan():   
    #Number of scaning rows (x):
    row=steps([1])
    #Number of scaning columns (y):
    col=steps([2])
    #Number of scanning planes (z):
    planes=steps([3])
    
    # length of empty matrix
    matrix_len=col*row
    data_array = np.zeros((matrix_len,col))
    plane=[]
    
    x_string = 'R1X' + str(row)
    y_string = 'R1Y' + str(col)
    z_string = 'R1Z' + str(planes)
    
    # print(ser_port.inWaiting()) 
    time.sleep(1) #min. 1 sek buffer at beginning of code
    for j in range(planes):
        string =str(j)
        y_pos=steps([2])
        ii=0
        with open('3D_Data_'+string+'.txt', 'w'):
            x_pos=steps([1])
            for i in range(matrix_len):
                if ii<col:
                    time.sleep(1.7) #Seems like it needs min. 1.7sek buffer between new commands to an axis 
                    ser_port.write(encoder(x_string))
                    df = pd.read_csv('Sample.csv',skiprows=14, delimiter='\t')
                    #print(df)
                    # powerdBm = df.loc[df.index[-1],'Power (dBm)'] #get Power (dBm) of last row in csv
                    powerdB = df.loc[df.index[-1],'Power (W)'] #get Power (W) of last row in csv
                    # print(powerdB)
                    #Logical entrees
                    #mean = 1
                    #stddev = 0.1
                    # powerdB=np.random.normal(loc=mean, scale=stddev, size=None)
                    data_array[i,:]=[y_pos,x_pos,powerdB]
                    x_pos+=x_pos
                    ii+=1
                    
                else:
                    time.sleep(1.7)
                    ser_port.write(homer('X',x_pos))
                    x_pos=steps([1])
                    time.sleep(1.7)
                    ser_port.write(encoder(y_string))
                    y_pos+=y_pos
                    ii=0
            # data = np.stack(data_array,axis=-1)
            # np.savetxt(file,data_array,fmt='%.4e')
            print(data_array,'\n')
    
    time.sleep(1) #min. 1 sek buffer at end of code
    
    
    #ser_port.close() 

    
#%% Window GUI
  
ro ot1 = tk.Tk()
root1.config(background='white')
root1.title('Control window')
root1.geometry('500x250')

###x-Entries

xtitle=tk.Label(root1, fg="blue",text="Step x (um)" )
xtitle.grid(row=0,column=0, padx=10, pady=5)

xEntry1=tk.Entry(root1, bg='white')
xEntry1.grid(row=0,column=1, padx=10, pady=5)
xEntry1.delete(0,tk.END)
xEntry1.insert(0,str(1))

xcounttitle=tk.Label(root1, fg="blue",text="No x-steps" )
xcounttitle.grid(row=0,column=2, padx=10, pady=5)

xcountEntry1=tk.Entry(root1, bg='white')
xcountEntry1.grid(row=0,column=3, padx=5, pady=5)
xcountEntry1.delete(0,tk.END)
xcountEntry1.insert(0,str(5))

xbutton=tk.Button(root1,text='Ok',bg='blue',command=xwriter)
xbutton.grid(row=0,column=4 ,padx=10, pady=5)

###y-Entries

ytitle=tk.Label(root1, fg="blue",text="Step y (um)" )
ytitle.grid(row=1,column=0, padx=10, pady=5)

yEntry1=tk.Entry(root1, bg='white')
yEntry1.grid(row=1,column=1, padx=10, pady=5)
yEntry1.delete(0,tk.END)
yEntry1.insert(0,str(1))

ycounttitle=tk.Label(root1, fg="blue",text="No y-steps" )
ycounttitle.grid(row=1,column=2, padx=10, pady=5)

ycountEntry1=tk.Entry(root1, bg='white')
ycountEntry1.grid(row=1,column=3, padx=10, pady=5)
ycountEntry1.delete(0,tk.END)
ycountEntry1.insert(0,str(5))

ybutton=tk.Button(root1,text='Ok',bg='red',command=ywriter)
ybutton.grid(row=1,column=4 ,padx=10, pady=5)

###z-Entries

ztitle=tk.Label(root1, fg="blue",text="Step z (um)" )
ztitle.grid(row=2,column=0, padx=10, pady=5)

zEntry1=tk.Entry(root1, bg='white')
zEntry1.grid(row=2,column=1, padx=10, pady=5)
zEntry1.delete(0,tk.END)
zEntry1.insert(0,str(1))

zcounttitle=tk.Label(root1, fg="blue",text="No z-steps" )
zcounttitle.grid(row=2,column=2, padx=10, pady=5)

zcountEntry1=tk.Entry(root1, bg='white')
zcountEntry1.grid(row=2,column=3, padx=10, pady=5)
zcountEntry1.delete(0,tk.END)
zcountEntry1.insert(0,str(5))

zbutton=tk.Button(root1,text='Ok',bg='green',command=zwriter)
zbutton.grid(row=2,column=4 ,padx=10, pady=5)


### scan button 

gobutton=tk.Button(root1,text='Scan',bg='grey',command=scan)
gobutton.grid(row=3,column=2 ,padx=10, pady=5)
root1.mainloop()
ser_port.close()
    



    
    
    
   
