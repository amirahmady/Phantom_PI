import threading
import csv
import threading


def myPeriodicFunction(data):
    print("This loops on a timer every {0} seconds".format(interval))

def startTimer(data):
    threading.Timer(interval, startTimer(data)).start()
    myPeriodicFunction(data)

with open("trajectory.csv") as trajFile:
    reader = csv.reader(trajFile, delimiter='\t')
    next(reader) # skip header
    data = [r for r in reader]

interval = 0.5
startTimer(data)
