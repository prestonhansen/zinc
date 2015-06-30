import sys
import zmq
import ratchromadata_pb2
import photonHit_pb2
import random

context = zmq.Context().instance()

socket = context.socket(zmq.REQ)
socket.bind("tcp://*:5555")

chromaSocket = context.socket(zmq.REQ)
chromaSocket.bind("tcp://*:5556")
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


def Server():
    print "opened"
    while True:
        #send the queuer our identity.
        socket.send(b"")
        num_pmts = int(socket.recv())
        print "got num. of pmts: ",num_pmts
    
        # get data for chroma
        socket.send(b"")
        msg = socket.recv()
        mychromadata = ratchromadata_pb2.ChromaData()
        mychromadata.ParseFromString(msg)
        print mychromadata, "\n"
        print "message size: ",mychromadata.ByteSize()
        
        chromaSocket.send(msg)
        print "sent to chroma"
        #generate some photons
        #phits = MakePhotons(num_pmts)
        #print "making some fake photons\n"
        #print phits
        #ship em
        #socket.send(phits.SerializeToString())    
        phits = photonHit_pb2.PhotonHits()
        phits = chromaSocket.recv()
        print phits
        print "got new data, sending to queue"
        socket.send(phits)
        socket.recv()
Server()
