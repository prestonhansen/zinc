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
import photonHit_pb2

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
def GenScintPhotons(protoString):
    nsphotons = 0
    for i,sData in enumerate(protoString.stepdata):
        nsphotons += sData.nphotons
    print "NSPHOTONS: ",nsphotons
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
    
def MakePhotonMessage(events):
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
                print "hit detID:",channelhit[n]," pos=",ev.photons_end.pos[n,:]," time=",ev.photons_end.t[n]

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
            aphoton.origin = photonHit_pb2.Photon.CHROMA 
    return phits
def main():
    while True:
        socks = dict(poll_Server.poll())
        
        if socks.get(backend) == zmq.POLLIN:
            optics = backend.recv()
            print optics
            backend.send(b'')
            msg = backend.recv()#_multipart()
            #^decide whether to use multipart or not^
            if not msg:
                break
            
            chromaData = ratchromadata_pb2.ChromaData()
            chromaData.ParseFromString(msg)
            print chromaData

            photons = GenScintPhotons(chromaData)
            
            """for cherenkov photons"""
            #if there are cherenkov photons, simulate and add them to the message
            #before it's sent back.
            
            # nphotons = sum(1 for p in enumerate(chromaData.stepdata))
            # if nphotons > 0:
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
            phits = MakePhotonMessage(events)
            print phits
            #ship it
            backend.send(phits.SerializeToString())
            
if __name__ == "__main__":
    main()
