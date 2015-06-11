import sys
import zmq
import time
import numpy as np


context = zmq.Context()

port = '5555'
socket = context.socket(zmq.REQ)
socket.connect( "tcp://localhost:%s" % (port) )


def Signal():
    print "Sending signal at port %s"%(port)
    socket.send(b"a")
    signal = socket.recv()
    print signal
    if signal is not None:
        socket.send(b"a")
        return True
    
    
def SendJob():
    #identifier
    print socket.recv()
    socket.send(b"some int")
    print socket.recv()
    socket.send(b"test")
def ReceiveInfo():
    signal = socket.recv()
    if signal == "DATA":
        socket.send(b"go")
        newData1 = socket.recv()
        socket.send(b"go")
        newData2 = socket.recv()
        print "New Data: ",newData1,"\nNew Data: ",newData2

def main():
    if Signal():
        SendJob()
    else:
        print "couldn't connect"
        exit(1)
    ReceiveInfo()

if __name__ == "__main__":
    main()
