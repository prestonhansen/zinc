import os, sys, time
import zmq
import chroma.api as api
api.use_cuda()
import numpy as np
from chroma.sim import Simulation
from chroma.event import Photons
import chroma.event

from uboone import uboone

import ratchromadata_pb2
#import photonHit_pb2

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
            msg = backend.recv()#_multipart()
            #^decide whether to use multipart or not^
            if not msg:
                break
            
            chromaData = ratchromadata_pb2.ChromaData()
            chromaData.ParseFromString(msg)
            
            dir = np.zeros((chromaData.cherenkovdata_size(),3), 
                           dtype = np.float32)
            for i in chromaData.cherenkovdata_size():
                dir[i,0] = chromaData.cherenkovdata(i).dx()
                dir[i,1] = chromaData.cherenkovdata(i).dy()
                dir[i,2] = chromaData.cherenkovdata(i).dz()
            pol = np.zeros_like(dir)
            for i in chromaData.cherenkovdata_size():
                pol[i,0] = chromaData.cherenkovdata(i).px()
                pol[i,1] = chromaData.cherenkovdata(i).py()
                pol[i,2] = chromaData.cherenkovdata(i).pz()
            
            pos = np.zeros_like(dir)
            for i in chromaData.cherenkovdata_size():
                pos[i,0] = chromaData.cherenkovdata(i).x()
                pos[i,1] = chromaData.cherenkovdata(i).y()
                pos[i,2] = chromaData.cherenkovdata(i).z()
            
            t = np.zeros((chromaData.cherenkovdata_size(),1), 
                         dtype=np.float32)
            for i in chromaData.cherenkovdata_size():n
                t[i,0] = chromaData.cherenkovdata(i).t
            
            wavelength = np.zeros_like(t)
            for i in chromaData.cherenkovdata_size():
                wavelength[i,0] = chromaData.cherenkovdata(i).wavelength

            
            #ship to GPU, do some stuff, send data back
            det = uboone()
            
            sim = Simulation(det,geant4_processes=0,nthreads_per_block = 1, max_blocks = 1024)
            #get photons here, pack them, run sim
            photons = Photons(pos=pos, dir=dir, pol=pol, t=t,
                              wavelength = wavelength)

            events = sim.simulate(photons, keep_photons_end=True, max_steps=2000)
            
            for ev in events:
                nhits = ev.channels.hit["""something goes here"""]
                
if __name__ = "__main__":
    main()
