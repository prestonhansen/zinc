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
#frontend = context.socket(zmq.ROUTER)
#backend = context.socket(zmq.DEALER)

#clients connect here
port = "5555"
socket = context.socket(zmq.ROUTER)
socket.bind( "tcp://*:%s"%(port))

#frontend.bind( "tcp://*:%s" % (port) )
#backend.bind( "tcp://*:5556" )

#zmq.device(zmq.QUEUE, frontend, backend)

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
    #maybe bad idea to have send use this structure
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

#talk to RAT clients, pull information about jobs
def Manager():
    print "Manager opened at port %s"%(port)
    while True:
        #wait for RAT client signal
        message = socket.recv_multipart()
        #print address
        print message
        print "Signal received from client"
        #send a signal to the client
        sendToRat(message[0],'test')
        time.sleep(0.25)
        
        #receive geometry from client
        #############################

        
        #receive job from client (make sure manager
        #differentiates between job and geometry)
        #get a signal that the client is ready to send 
        #job info (use some identifier)
        
        #ready to start pulling data
        jobSignal = socket.recv_multipart()
        print jobSignal
        if jobSignal[2] == 'a':
            sendToRat(jobSignal[0],'send')
            testID = getFromRat(jobSignal[0])
            sendToRat(jobSignal[0],'send')
            testInfo = getFromRat(jobSignal[0])
            print "Got data: ",testID,"  ", testInfo
        else:
            print "not ready"
        #ready signal for chroma
        sendToChroma("go")
        pub_socket.recv()
        #send data to chroma
        sendToChroma(testID)
        pub_socket.recv()
        sendToChroma(testInfo)
        pub_socket.recv()
        #ready to receive "processed" data
        sendToChroma("go")
        newData1 = getFromChroma()
        sendToChroma("go")
        newData2 = getFromChroma()
        #signal back to rat
        sendToRat(jobSignal[0],"DATA")
        #send the new data
        
        while True:
            if socket.recv_multipart()[2] == "go":
                sendToRat(jobSignal[0],newData1)
                break
            else:
                #do something else...wait etc
                print "RAT client not ready"
                time.sleep(1)
                print "trying again"
                sendToRat(jobSignal[0],"DATA")
        #check if rat is ready for more data
        socket.recv_multipart()
        sendToRat(jobSignal[0],"DATA")
        print 'y'
        while True:
            if socket.recv_multipart()[2] == "go":
                sendToRat(jobSignal[0],newData2)
                break
            else:
                #do something else...wait etc
                print "RAT client not ready"
                time.sleep(1)
                print "trying again"
                sendToRat(jobSignal[0],"DATA")
        print 'x'

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





    
