1;2cimport os, sys, time
import zmq
import numpy as np

import ratchromadata_pb2
#import photonHit_pb2
import hitPhotons_pb
import cProfile
import TChromaSimCython
context = zmq.Context().instance()

backend = context.socket(zmq.REP)

backport = '5556' #talks to REQ frontend of server (on backend)

backend.connect( "tcp://localhost:%s"%(backport) )

def main():
    optics = backend.recv()
    #print optics
    backend.send(b'')
    for x in xrange(5):
        msg = backend.recv()#_multipart()
        s = time.clock()
        chromaData = ratchromadata_pb2.ChromaData()
        chromaData.ParseFromString(msg)
        print "got chroma data: decode time=",time.clock()-s
        phits = TChromaSimCython.MakePhotonMessage(chromaData)
        stime = time.clock()
        backend.send(phits)
        etime = time.clock()
        print "TIME TO SER: ",(etime-stime)
        #print "sent data"
if __name__ == "__main__":
    cProfile.start("main()")
