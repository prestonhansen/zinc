import sys
import zmq
import time
import threading


context = zmq.Context().instance()

frontend = context.socket(zmq.ROUTER)
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
            if clients:
                #server wants data
                msg = frontend.recv_multipart()
                serverIdentity = msg[0]
                clientIdentity = clients.pop(0)
                print msg
                #is a check for a ready signal necessary?
                #i.e. will the server be querying the queue for
                #any other reason? 
                #probably for 'send back' requests, probably want to
                #write something else for that
                request = [clientIdentity, '', 'data']
                print request
                backend.send_multipart(request)
                data = backend.recv_multipart()
                print data
                time.sleep(1)
                frontend.send_multipart([serverIdentity,'',
                                         data[2],])
                newMsg = frontend.recv_multipart()
                print newMsg
                frontend.send_multipart([serverIdentity,'',''])
                newData = newMsg[2]
                backend.send_multipart([clientIdentity,'',newData])
                print 'sent'
            else:
                pass #do something
Queue()
