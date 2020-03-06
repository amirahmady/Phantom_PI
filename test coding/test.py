#!/usr/bin/env python3
import math
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

class Student(Person):
    def __init__(self, *args):
        super().__init__(self,args)
        self.graduationyear =  0
        self.t=0
    def calc(self,number):
        self.t=self.graduationyear+4
        return self.t


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
print(ordinal(2))

""" x = Student("Mike", "Olsen")
x.graduationyear=10
print(x.calc(4))
print(x.t) """