import sys
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5556")

def GetData():
    jobID = socket.recv()
    print "received job id %s"%(jobID)
    socket.send(b"")
    jobInfo = socket.recv()
    print "received info %s"%(jobInfo)
    #do some stuff
    socket.send(b"")
    sendBack(doSomething(jobID))
    sendBack(doSomething(jobInfo))
def doSomething(data1):
    reversed1 = data1[::-1]
    return reversed1
def sendBack(data1):
    signal = socket.recv()
    if signal == "go":
        socket.send(data1)

def main():
    GetData()


if __name__ == "__main__":
    main()
        
        
