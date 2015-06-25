import os, sys, time
nimport zmq
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
det = uboone()
            
sim = Simulation(det,geant4_processes=0,nthreads_per_block = 1, max_blocks = 1024)

def main():
    while True:
        socks = dict(poll_Server.poll())
        
        if socks.get(backend) == zmq.POLLIN:
            msg = backend.recv()#_multipart()
            #^decide whether to use multipart or not^
            if not msg:
                break
            
            chromaData = ratchromadata_pb2.ChromaData()
            chromaData.ParseFromString(msg)
            print chromaData
            nphotons = sum(1 for p in enumerate(chromaData.cherenkovdata))
            dphi = np.random.uniform(0,2.0*np.pi, nphotons)
            dcos = np.random.uniform(-1.0, 1.0, nphotons)
            dir = np.array( zip( np.sqrt(1-dcos[:]*dcos[:])*np.cos(dphi[:]), np.sqrt(1-dcos[:]*dcos[:])*np.sin(dphi[:]), dcos[:] ), dtype=np.float32 )

            print "NUMPHOTONS: ",nphotons
            """for cherenkov photons"""
            # dir = np.zeros((nphotons,3), 
            #               dtype = np.float32)
            # for i,cData in enumerate(chromaData.cherenkovdata):
            #   dir[i,0] = cData.dx()
            #     dir[i,1] = cData.dy()
            #     dir[i,2] = cData.dz()
            # pol = np.zeros_like(dir)
            # for i,cData in (chromaData.cherenkovdata):
            #     pol[i,0] = cData.px()
            #     pol[i,1] = cData.py()
            #     pol[i,2] = cData.pz()
            
            # pos = np.zeros_like(dir)
            # for i,cData in (chromaData.cherenkovdata):
            #     pos[i,0] = cData.x()
            #     pos[i,1] = cData.y()
            #     pos[i,2] = cData.z()
            
            # t = np.zeros((nphotons), 
            #              dtype=np.float32)
            # for i,cData in (chromaData.cherenkovdata):
            #     t[i] = cData.t()
            
            # wavelengths = np.zeros_like(t)
            # for i,cData in (chromaData.cherenkovdata):
            #     wavelengths[i] = cData.wavelengths()

            
            #ship to GPU, do some stuff, send data back
            photons = Photons(pos=pos, dir=dir, pol=pol, t=t,
                              wavelengths = wavelengths)

            events = sim.simulate(photons, keep_photons_end=True, max_steps=2000)
            
            for ev in events:
                detected_photons = ev.photons_end.flags[:] & chroma.event.SURFACE_DETECT
                channelhit = np.zeros(len(detected_photons),dtype=np.int)
                channelhit[:] = det.solid_id_to_channel_index[ det.solid_id[ev.photons_end.last_hit_triangles[:] ] ]
                for n,f in enumerate(detected_photons):
                    if f!=0:
                        print "hit detID:",channelhit[n]," pos=",ev.photons_end.pos[n,:]," time=",ev.photons_end.t[n]-100.0
                
if __name__ == "__main__":
    main()
