#queue/server
import sys
import zmq
import time
import threading
import ratchromadata_pb2
import photonHit_pb2
import random
#chroma
#import chroma.api as api
# api.use_cuda()
# import numpy as np
# from chroma.sim import Simulation
# from chroma.event import Photons
# import chroma.event

# from uboone import uboone

#det = uboone()

#sim = Simulation(det,geant4_processes=0,nthreads_per_block = 1, max_blocks = 1024)

#zinc
from multiprocessing import Process, Lock

############### CLIENT AND SERVER LAYERS ###############

def ChromaClient(l):
    context = zmq.Context().instance()

    backend = context.socket(zmq.REP)

    backport = '5556' #talks to REQ frontend of server (on backend)

    backend.connect( "tcp://localhost:%s"%(backport) )

    poll_Server = zmq.Poller()
    poll_Server.register(backend, zmq.POLLIN)
    #can set polling options to kill and restart on user input or
    #set a timeout

    #!!!!!!!!
    #need to decide whether det and sim will be global or passed through to
    #makephotonmessage function.
    #!!!!!!!!

    while True:
        socks = dict(poll_Server.poll())
        
        if socks.get(backend) == zmq.POLLIN:
            msg = backend.recv()#_multipart()
            #^decide whether to use multipart or not^
            if not msg:
                break
            
            chromaData = ratchromadata_pb2.ChromaData()
            chromaData.ParseFromString(msg)
            l.acquire()
            print chromaData
            l.release()

            photons = GenScintPhotons(chromaData,l)
            
            """for cherenkov photons"""
            #if there are cherenkov photons, simulate and add them to the message
            #before it's sent back.
            
            # nphotons = sum(1 for p in enumerate(chromaData.stepdata))
            # if nphotons > 0:

            ####USE LOCKING WHEN YOU UNCOMMENT THIS##########

            #     print "NUMPHOTONS: ",nphotons
            #     dir = np.zeros((nphotons,3), 
            #                    dtype = np.float32)
            #     for i,cData in enumerate(chromaData.cherenkovdata):
            #         dir[i,0] = cData.dx()
            #         dir[i,1] = cData.dy()
            #         dir[i,2] = cData.dz()
            #         pol = np.zeros_like(dir)
            #         for i,cData in (chromaData.cherenkovdata):
            #             pol[i,0] = cData.px()
            #             pol[i,1] = cData.py()
            #             pol[i,2] = cData.pz()
                        
            #         pos = np.zeros_like(dir)
            #         for i,cData in (chromaData.cherenkovdata):
            #             pos[i,0] = cData.x()
            #             pos[i,1] = cData.y()
            #             pos[i,2] = cData.z()
                
            #         t = np.zeros((nphotons), 
            #                      dtype=np.float32)
            #         for i,cData in (chromaData.cherenkovdata):
            #             t[i] = cData.t()
                    
            #         wavelengths = np.zeros_like(t)
            #         for i,cData in (chromaData.cherenkovdata):
            #             wavelengths[i] = cData.wavelengths()
                
            #         #ship to GPU, do some stuff, send data back
            #         photons = Photons(pos=pos, dir=dir, pol=pol, t=t,
            #                   wavelengths = wavelengths)

            events = sim.simulate(photons, keep_photons_end=True, max_steps=2000)
            #pack hitphoton data into protobuf
            phits = MakePhotonMessage(events,l)
            l.acquire()
            print phits
            l.release()
            #ship it
            backend.send(phits.SerializeToString())

def Queue(l):

    context = zmq.Context().instance()

    frontend = context.socket(zmq.ROUTER)
    backend = context.socket(zmq.ROUTER)

    frontport = '5555'

    backport = '5554'

    frontend.connect( "tcp://localhost:%s"%(frontport) ) #talk to server
    backend.bind( "tcp://*:%s"%(backport) ) #talk to clients

    poll_RAT = zmq.Poller()
    poll_RAT.register(backend, zmq.POLLIN)
    poll_both = zmq.Poller()
    poll_both.register(backend, zmq.POLLIN)
    poll_both.register(frontend, zmq.POLLIN)

    clients = []
    while True:
        if clients:
            socks = dict(poll_both.poll())
        else:
            socks = dict(poll_RAT.poll(3000))#timeout in ms
        
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
                l.acquire()
                print msg
                l.release()
                #get detector config
                requestConfig = [clientIdentity, '', 'cfg']
                l.acquire()
                print requestConfig
                l.release()
                backend.send_multipart(requestConfig)
                cfg = backend.recv_multipart()
                l.acquire()
                print cfg
                l.release()
                #send detector config
                frontend.send_multipart([serverIdentity,'',cfg[2],])
                frontend.recv_multipart()
                #get data
                requestData = [clientIdentity, '', 'data']
                backend.send_multipart(requestData)
                data = backend.recv_multipart()
                #send data
                frontend.send_multipart([serverIdentity,'',data[2],])
                #get processed data back
                newMsg = frontend.recv_multipart()
                #l.acquire()
               # print newMsg
                #l.release()
                newData = newMsg[2]
                l.acquire()
                print "got new data"
                l.release()
                #send ok signal to server
                frontend.send_multipart([serverIdentity,'',''])
                #send processed data back to client
                backend.send_multipart([clientIdentity,'',newData])
                l.acquire()
                print 'sent to RAT'
                l.release()
        else:
            pass #(this stuff doesn't work right yet)
            # l.acquire()
            # print "no response, restarting and trying again...\n"
            # l.release()
            # frontend.setsockopt(zmq.LINGER,0)
            # frontend.close()
            # poll_both.unregister(frontend)
            # frontend = context.socket(zmq.ROUTER)
            # frontend.connect( "tcp://localhost:%s"%(frontport) ) #talk to server

def Server(l):
    context = zmq.Context().instance()

    socket = context.socket(zmq.REQ)
    socket.bind("tcp://*:5555")

    chromaSocket = context.socket(zmq.REQ)
    chromaSocket.bind("tcp://*:5556")
    
    l.acquire()
    print "opened"
    l.release()
    f = open('MESSAGESIZE','w')
    while True:
        #send the queuer our identity.
        socket.send(b"")
        num_pmts = int(socket.recv())
        l.acquire()
        print "got num. of pmts: ",num_pmts
        l.release()

        # get data for chroma
        socket.send(b"")
        msg = socket.recv()
        mychromadata = ratchromadata_pb2.ChromaData()
        mychromadata.ParseFromString(msg)
        #print mychromadata, "\n"
        #print "message size: ",mychromadata.ByteSize()
        f.write(str(mychromadata.ByteSize())+'\n')
        
        chromaSocket.send(msg)
        l.acquire()
        print "sent to chroma"
        l.release()
        #generate some photons
        #phits = MakePhotons(num_pmts)
        #print "making some fake photons\n"
        #print phits
        #ship em
        #socket.send(phits.SerializeToString())    
        phits = photonHit_pb2.PhotonHits()
        phits = chromaSocket.recv()
        #print phits
        #print "bytesize: ",phits.ByteSize()
        l.acquire()
        print "got new data, sending to queue"
        l.release()
        socket.send(phits)
        socket.recv()


############### END CLIENT AND SERVER LAYERS ###############

############### FUNCTIONS USED BY CLIENT AND NETWORKING LAYERS ###############

#used by chroma
#passes in a protobuf string object; returns a Photons object to be used
#by chroma in Simulate()
def GenScintPhotons(protoString,l):
    nsphotons = 0
    for i,sData in enumerate(protoString.stepdata):
        nsphotons += sData.nphotons
    l.acquire()
    print "NSPHOTONS: ",nsphotons
    l.release()
    pos = np.zeros((nsphotons,3),dtype=np.float32)
    pol = np.zeros_like(pos)
    t = np.zeros(nsphotons, dtype=np.float32)
    wavelengths = np.empty(nsphotons, np.float32)
    wavelengths.fill(128.0)
    dphi = np.random.uniform(0,2.0*np.pi, nsphotons)
    dcos = np.random.uniform(-1.0, 1.0, nsphotons)
    dir = np.array( zip( np.sqrt(1-dcos[:]*dcos[:])*np.cos(dphi[:]), np.sqrt(1-dcos[:]*dcos[:])*np.sin(dphi[:]), dcos[:] ), dtype=np.float32 )
    stepPhotons = 0
    for i,sData in enumerate(protoString.stepdata):
        #instead of appending to array every loop, the full size (nsphotons x 3) is allocated to begin, then 
        #values are filled properly by incrementing stepPhotons.
        for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
            pos[j,0] = np.random.uniform(sData.step_start_x,sData.step_end_x)
            pos[j,1] = np.random.uniform(sData.step_start_y,sData.step_end_y)
            pos[j,2] = np.random.uniform(sData.step_start_z,sData.step_end_z)
        for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
            pol[j,0] = np.random.uniform(0,((1/3.0)**.5))
            pol[j,1] = np.random.uniform(0,((1/3.0)**.5))
            pol[j,2] = ((1 - pol[j,0]**2 - pol[j,1]**2)**.5)
        for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
            t[j] = (np.random.exponential(1/45.0) + (sData.step_end_t-sData.step_start_t))
        stepPhotons += sData.nphotons
    return Photons(pos = pos, pol = pol, t = t, dir = dir, wavelengths = wavelengths)

#used by chroma
#passes in an events object generated by the chroma sim; returns a photonHit_pb2.PhotonHits()
#message that can have protobuf methods applied to it (serialization)
def MakePhotonMessage(events,l):
    phits = photonHit_pb2.PhotonHits()
    for ev in events:
        detected_photons = ev.photons_end.flags[:] & chroma.event.SURFACE_DETECT
        channelhit = np.zeros(len(detected_photons),dtype=np.int)
        channelhit[:] = det.solid_id_to_channel_index[ det.solid_id[ev.photons_end.last_hit_triangles[:] ] ]
        phits.count = int(np.count_nonzero(detected_photons))
        for n,f in enumerate(detected_photons):
            if f==0:
                continue
            else:
                l.acquire()
                print "hit detID:",channelhit[n]," pos=",ev.photons_end.pos[n,:]," time=",ev.photons_end.t[n]
                l.release()

            aphoton = phits.photon.add()
            aphoton.PMTID = int(channelhit[n])
            aphoton.Time = float(ev.photons_end.t[n])
            aphoton.KineticEnergy = float((2*(np.pi)*(6.582*(10**-16))*(299792458.0))/(ev.photons_end.wavelengths[n]))
            aphoton.posX = float(ev.photons_end.pos[n,0])
            aphoton.posY = float(ev.photons_end.pos[n,1])
            aphoton.posZ = float(ev.photons_end.pos[n,2])
            # px = |p|*cos(theta) = (h / lambda)*(<u,v> / |u||v|) = (h / lambda)*(u1 / |u|), etc.
            #turns out we don't need to to this... px = |p|*phat = (h / lambda) * (dir[n,0]...etc.
            aphoton.momX = float(((4.135667516 * (10**-21))/(ev.photons_end.wavelengths[n])) * (ev.photons_end.dir[n,0]))
            aphoton.momY = float(((4.135667516 * (10**-21))/(ev.photons_end.wavelengths[n])) * (ev.photons_end.dir[n,1]))
            aphoton.momZ = float(((4.135667516 * (10**-21))/(ev.photons_end.wavelengths[n])) * (ev.photons_end.dir[n,2]))
            aphoton.polX = float(ev.photons_end.pol[n,0])
            aphoton.polY = float(ev.photons_end.pol[n,1])
            aphoton.polZ = float(ev.photons_end.pol[n,2])
            aphoton.origin = photonhit_pb2.Photon.CHROMA 
    return phits

#OPTIONAL: can be used by networking layers for debugging purposes.
#returns a photonHit_pb2.PhotonHits() object. 
def MakePhotons(num_pmts):
    phits = photonHit_pb2.PhotonHits()
    pmt_id = 0
    for x in xrange (0,num_pmts):
        pmt_id += 1
        aphoton = phits.photon.add()
        aphoton.count = 1
        for x in xrange (0, aphoton.count):
            aphoton.PMTID = pmt_id
            aphoton.Time = random.uniform(0,30)
            aphoton.KineticEnergy = random.uniform(2.61*(10**-6),3.22*(10**-6))
            #converted to MeV
            aphoton.posX = random.uniform(-1,1)
            aphoton.posY = random.uniform(-1,1)
            aphoton.posZ = random.uniform(-1,1)
            aphoton.momX = ((aphoton.KineticEnergy/3.0)
                                 **0.5)
            aphoton.momY = ((aphoton.KineticEnergy/3.0)
                                 **0.5)
            aphoton.momZ = ((aphoton.KineticEnergy/3.0)
                                 **0.5)
            aphoton.polX = random.uniform(0,((1/3.0)**.5))
            aphoton.polY = random.uniform(0,((1/3.0)**.5))
            aphoton.polZ = ((1 - aphoton.polX**2 -
                                  aphoton.polY**2)**.5)
            aphoton.trackID = random.randint(0,25)
            aphoton.origin = 4
    return phits

############### END FUNCTIONS USED BY CLIENT AND NETWORKING LAYERS ###############    

############### MAIN ###############
if __name__ == "__main__":
    lock = Lock()
    #chromaProcess = Process(target=ChromaClient, args=(lock,))
    #chromaProcess.start()

    queue = Process(target=Queue,args=(lock,))
    queue.start()

    server = Process(target=Server,args=(lock,))
    server.start()

    
