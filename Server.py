#########################
########changelog########
#########################
#06/09/15
#0.0: wrote some code:
#can successfully send a file from RAT client to server to chroma client,
#do something, and send it back to the server then RAT.
import sys
import zmq
import time
import threading
#import protobuf (not yet...let's make it do stuff first!)
#import numpy as np (not yet)

context = zmq.Context()
#frontend = context.socket(zmq.ROUTER)
#backend = context.socket(zmq.DEALER)
port = "5555"
socket = context.socket(zmq.REP)
socket.bind( "tcp://*:%s"%(port))
#RAT clients connect here
#frontend.bind( "tcp://*:%s" % (port) )
#backend.bind( "tcp://*:5556" )

#zmq.device(zmq.QUEUE, frontend, backend)

#stuff gets sent to chroma here
publish_port = "5556"
pub_socket = context.socket(zmq.REQ) #can this be pub? needs to send and receive. receive on 5555? 
pub_socket.bind( "tcp://*:%s" % (publish_port) )


#talk to RAT clients, pull information about jobs
def Manager():
    print "Manager opened at port %s"%(port)
    while True:
        #wait for RAT client signal
        signal = socket.recv()
        print "Signal received from client"
        #send a signal to the client
        socket.send(b"test")
        time.sleep(1)

        #something goes here to make sure that the client 
        #received the signal and is ready to send a job and
        #some geometry
        
        #receive geometry from client
        #############################

        
        #receive job from client (make sure manager
        #differentiates between job and geometry)
        #get a signal that the client is ready to send job info (use some identifier)
        jobSignal = socket.recv()
        if jobSignal is not None:
            socket.send(b"send the ID")
            time.sleep(1)
            testID = socket.recv()
            socket.send(b"send the info")
            time.sleep(1)
            testInfo = socket.recv()
            print testID,"  ", testInfo
            print "sending to chroma..\n"
            
            pub_socket.send(testID)
            pub_socket.recv()
            pub_socket.send(testInfo)
            time.sleep(3)
            """#client ready to send job, take its messages and make a job for chroma
            ID = socket.recv()
            info = socket.recv()
            someJob = Job(ID, info)
            
            npJobtype = np.dtype(Job(-1,'null'))
            npJob =""" 
        else:
            print "client not ready to send job"
        #get data back from chroma
        pub_socket.recv()
        pub_socket.send(b"go")
        newData1 = pub_socket.recv()
        print newData1
        pub_socket.send(b"go")
        newData2 = pub_socket.recv()
        print newData2
        #send it back to RAT
        socket.send(b"DATA")
        socket.recv()
        socket.send(newData1)
        socket.recv()
        socket.send(newData2)

class Job:
    def __init__(self, jobID, jobInfo):
        #TBD (what would a default constructor look like?)
        #(do we need multiple constructors?)
        #do jobs share common class data?
        self.jobID = jobID
        self.jobInfo = jobInfo
Manager()
#class Event:
    #magic goes here
