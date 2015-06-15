import sys
import zmq
import time
import threading


context = zmq.Context().instance()

frontend = context.socket(zmq.DEALER)
backend = context.socket(zmq.ROUTER)

frontport = '5555'

backport = '5554'

frontend.connect( "tcp://localhost:%s"%(frontport) )
backend.bind( "tcp://*:%s"%(backport) )

poll_RAT = zmq.Poller()
poll_RAT.register(backend, zmq.POLLIN)
poll_both = zmq.Poller()
poll_both.register(backend, zmq.POLLIN)
poll_both.register(frontend, zmq.POLLIN)

clients = []

def Queue():
    while True:
        if clients:
            socks = dict(poll_both.poll())
        else:
            socks = dict(poll_RAT.poll())
        
        if socks.get(backend) == zmq.POLLIN:
            msg = backend.recv_multipart()
            if not msg:
                break
            address = msg[0]
            clients.append(address)
            
            #want to sort replies so the dealer isn't sending
            #stuff that shouldnt be sent to the server
            #i.e. if msg == .. etc 
        if socks.get(frontend) == zmq.POLLIN:
            msg = frontend.recv_multipart()
            #is a check for a ready signal necessary?
            #i.e. will the server be querying the queue for
            #any other reason? 
            #probably for 'send back' requests, probably want to
            #write something else for that
            request = [clients.pop(0), ''] + msg
            frontend.send_multipart(request)
            
