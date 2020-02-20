import numpy as np
import matplotlib.pyplot as plt


class Sine_Wave:
    def __init__(self,A,f,t,res,phase):
        self.A = A
        self.f= f
        self.t= np.arange(0,t,res)
        self.phase= phase    
        self.phi= phase*np.pi
        self.calc_x()       
    def calc_x(self):
        self.x = self.A*np.sin(2*np.pi*self.f*self.t + self.phi)
    def show_plot(self,x0=0,x1=8,y0=-5,y1=5):   #0,8,-5,5   
        #self.calc_x()
        plt.plot(self.t,self.x)
        plt.axis([x0,x1,y0,y1])
        plt.xlabel('time in seconds')
        plt.ylabel('amplitude')
        plt.show()

if  __name__ == "__main__":
    s1=Sine_Wave(3,.25,8,0.01,0)
    s1.show_plot()