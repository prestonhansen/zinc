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
        RATclient.recv()
        SendJob(RATclient,'some int')
        RATclient.recv()
        SendJob(RATclient,'some other data')
    else:
        print "couldn't connect"
        exit(1)
    print "New Data: ",ReceiveInfo(RATclient, RATclient.recv())
    RATclient.send(b"")
    print "New Data: ",ReceiveInfo(RATclient, RATclient.recv())

def Signal(socket):
    print "Sending signal at port %s"%(port)
    socket.send(b"EV")
    signal = socket.recv()
    print signal
    if signal is not None:
        socket.send(b"a")
        return True
        
def SendJob(socket,data):
    print "sending"
    socket.send(data)
# later on probably want to use multipart messages and something
#like: if is_more: receive info, if signal == something sendJob  
def ReceiveInfo(socket, signal):
    if signal == "DATA":
        socket.send(b"go")
        newData = socket.recv()
    else:
        print "error, exiting" 
        exit(1)
    return newData
def main():
    for i in range(NUMBER_OF_CLIENTS):
        Thread(target=RAT_Thread).start()

if __name__ == "__main__":
    main()
