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
        if socks.get(frontend) == zmq.POLLIN:
            if clients:
                #server wants data
                msg = frontend.recv_multipart()
                serverIdentity = msg[0]
                clientIdentity = clients.pop(0)
                print msg
                #get detector config
                requestConfig = [clientIdentity, '', 'cfg']
                print requestConfig
                backend.send_multipart(requestConfig)
                cfg = backend.recv_multipart()
                print cfg
                #send detector config
                frontend.send_multipart([serverIdentity,'',
                                         cfg[2],])
                frontend.recv_multipart()
                #get data
                requestData = [clientIdentity, '', 'data']
                backend.send_multipart(requestData)
                data = backend.recv_multipart()
                #send data
                frontend.send_multipart([serverIdentity,'',
                                         data[2],])
                #get processed data back
                newMsg = frontend.recv_multipart()
                newData = newMsg[2]
                #send processed data back to client
                backend.send_multipart([clientIdentity,'',newData])
                print 'sent'
            else:
                pass #do something
Queue()
