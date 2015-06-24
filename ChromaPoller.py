import os, sys, time
import zmq
import chroma.api as api
api.use_cuda()

import numpy as np
from chroma.sim import Simulation
from chroma.event import Photons
import chroma.event

from uboone import uboone

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
            
                
            #pack received data into numpy array

            #ship to GPU, do some stuff, send data back
            det = uboone()
            
            sim = Simulation(det,geant4_processes=0,nthreads_per_block = 1, max_blocks = 1024)
            #get photons here, pack them, run sim
            nphotons = -1 #need to grab count from rat
            
            photons = -1 #get these from RAT (cerenkov)
            events = sim.simulate(photons, keep_photons_end=True, max_steps=2000)
            
            for ev in events:
                nhits = ev.channels.hit["""something goes here"""]
                
if __name__ = "__main__":
    main()
