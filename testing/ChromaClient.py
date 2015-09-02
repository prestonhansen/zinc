import sys
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5556")

def GetData():
    data = socket.recv()
    print "received data %s"%(data)
    return data
def doSomething(data1):
    reversed1 = data1[::-1]
    return reversed1
def sendBack(data1):
    print "sending data back"
    signal = socket.recv()
    if signal == "go":
        socket.send(data1)
def sendSignal(somestring):
    socket.send(somestring)
def waitForSignal():
    msg = socket.recv()
    return msg

def main():
    if waitForSignal() is not None:
        sendSignal("")
        jobID = GetData()
        sendSignal("")
        sendBack(doSomething(jobID))
        exit(1)
    else:
        main()


if __name__ == "__main__":
    main()
        
        
    

