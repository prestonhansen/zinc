import sys
import zmq
import time



context = zmq.Context().instance()


backend = context.socket(zmq.REP)

backport = '5556' #talks to REQ frontend of server (on backend)


backend.connect( "tcp://localhost:%s"%(backport) )

poll_Server = zmq.Poller()
poll_Server.register(backend, zmq.POLLIN)
#can set polling options to kill and restart on user input or
#set a timeout
def main():
    while True:
        socks = dict(poll_RAT.poll())
        
        if socks.get(backend) == zmq.POLLIN:
            msg = backend.recv#_multipart()
            #^decide whether to use multipart or not^
            if not msg:
                break
            
            #pack received data into numpy array

            #ship to GPU, do some stuff, send data back

            
if __name__ = "__main__":
    main()
