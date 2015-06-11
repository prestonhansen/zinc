import sys
import zmq
import time
#import numpy as np
from threading import Thread
from random import randint


#context = zmq.Context()

port = '5555'
#socket = context.socket(zmq.REQ)
#socket.connect( "tcp://localhost:%s" % (port) )

NUMBER_OF_CLIENTS = 1 #doesn't scale properly yet
def set_id(zsocket):
    """Set simple random printable identity on socket"""
    identity = u"%04x-%04x" % (randint(0, 0x10000), randint(0, 0x10000))
    
    zsocket.setsockopt_string(zmq.IDENTITY, identity)

def RAT_Thread(context=None):
    context = context or zmq.Context.instance()
    RATclient = context.socket(zmq.REQ)
    set_id(RATclient)
    RATclient.connect("tcp://localhost:5555")
    if Signal(RATclient):
        SendJob(RATclient)
    else:
        print "couldn't connect"
        exit(1)
    ReceiveInfo(RATclient)

def Signal(socket):
    print "Sending signal at port %s"%(port)
    socket.send(b"z")
    signal = socket.recv()
    print signal
    if signal is not None:
        socket.send(b"a")
        return True
        
def SendJob(socket):
    #identifier
    print socket.recv()
    socket.send(b"some int")
    print socket.recv()
    socket.send(b"test")
# later on probably want to use multipart messages and something
#like: if is_more: receive info, if signal == something sendJob  
def ReceiveInfo(socket):
    signal = socket.recv()
    if signal == "DATA":
        socket.send(b"go")
        newData1 = socket.recv()
        socket.send(b"go")
        newData2 = socket.recv()
        print "New Data: ",newData1,"\nNew Data: ",newData2

def main():
    for i in range(NUMBER_OF_CLIENTS):
        Thread(target=RAT_Thread).start()

if __name__ == "__main__":
    main()
