#########################
########changelog########
#########################
#06/09/15
#0.0: wrote some code
#06/10/15
#0.0001: cleaned stuff up, condensed common operations into
#functions. 
#0.0002 rewrote server to handle RAT clients as router type (asynchronous)
#
import sys
import zmq
import time
import threading
#import protobuf (not yet...let's make it do stuff first!)
#import numpy as np (not yet)

context = zmq.Context().instance()

#clients connect here
port = "5555"
socket = context.socket(zmq.REQ)
socket.bind( "tcp://*:%s"%(port))


#stuff gets sent to chroma here
publish_port = "5556"
pub_socket = context.socket(zmq.REQ) 
pub_socket.bind( "tcp://*:%s" % (publish_port) )

def serverWait():
    return True
    #define this function to send a "wait"
    #signal to the respective clients?
    #pass in (a) target client(s) to issue wait loop to?
def getFromRat(address):
    message = socket.recv_multipart() 
    print message
    return message[2]
def sendToChroma(data):
    print "sending to chroma\n"
    pub_socket.send(data)
    #define send and receive functions to return true
    #if successful?
    #check for send/receive state at beginning of send/receive
    #functions ??
def getFromChroma():
        newData = pub_socket.recv()
        print "New data: ",newData
        return newData
def sendToRat(address,data):
    print "sending to RAT\n"
    socket.send_multipart([
        address,
        b'',
        data,
    ])
    #want to check for failure here ?? 
def getEventInfo(address,socket):
    jobSignal = socket.recv_multipart()
    print jobSignal
    if jobSignal[2] == 'a':
        sendToRat(jobSignal[0],'send')
        testID = getFromRat(jobSignal[0])
        sendToRat(jobSignal[0],'send')
        testInfo = getFromRat(jobSignal[0])
        print "Got data: ",testID,"  ", testInfo
        return testID, testInfo
        #multiple return structure should be ok if we know the
        #format of the data we're getting back
    else:
        print "not ready, trying again"
        time.sleep(.5)
        sendToRat(jobSingal[0],'EV')
        getEventInfo(jobSignal[0],socket)
#talk to RAT clients, pull information about jobs
def Manager():
    print "Manager opened at port %s"%(port)
    #request data
    while True:
        socket.send(b'test')
        print 'sent signal'
        data = socket.recv()
        print 'got msg: ',data
        sendToChroma('')
        pub_socket.recv()
        sendToChroma(data)
        pub_socket.recv()
        sendToChroma('go')
        newData = getFromChroma()
        socket.send(newData)
        socket.recv()
class Job:
    def __init__(self, jobID, jobInfo):
        #TBD (what would a default constructor look like?)
        #(do we need multiple constructors?)
        #do jobs share common class data?
        self.jobID = jobID
        self.jobInfo = jobInfo
def main():
    try:
        Manager()
    except (KeyboardInterrupt, SystemExit):
        print "\nReceived keyboard interrupt, exiting\n"
        exit(1)
        
#class Event:
    #magic goes here

if __name__ == "__main__":
    main()





    
