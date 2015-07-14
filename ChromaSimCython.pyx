from cprotobuf import encode_data
import photonHit_pb2
import ratchromadata_pb2
from hitPhotons_pb import PhotonHits
import numpy as np

import chroma.api as api
api.use_cuda()
from chroma.sim import Simulation
from chroma.event import Photons
import chroma.event

from uboone import uboone

cimport numpy as np
import time

import cython
cimport cython

cdef extern void C_MessagePack(int* PMTArr, float* TimeArr, float* WaveArr, float* PosArr, float* DirArr, float* PolArr, hitPhotons::PhotonHits fPhotonData, int nphotons)


DTYPEINT = np.int
ctypedef np.int_t DTYPEINT_t
DTYPEFLOAT32 = np.float32
ctypedef np.float32_t DTYPEFLOAT32_t
DTYPEUINT16 = np.uint16
ctypedef np.uint16_t DTYPEUINT16_t
det = uboone()

sim = Simulation(det,geant4_processes=0,nthreads_per_block = 1, max_blocks = 1024)

@cython.boundscheck(False)
def MessagePack(np.ndarray[DTYPEFINT_t, ndim = 1, mode = "c"], np.ndarray[DTYPEFLOAT32_t, ndim = 1, mode = "c"], np.ndarray[DTYPEFLOAT32_t, ndim = 2, mode = "c"], np.ndarray[DTYPEFLOAT32_t, ndim = 2, mode = "c"], np.ndarray[DTYPEFLOAT32_t, ndim = 2, mode = "c"], np.ndarray[DTYPEFLOAT32_t, ndim = 2, mode = "c"], fPhotonData, nphotons):
    C_MessagePack(&input[0],&input[0],&input[0],&input[0,0],&input[0,0],&input[0,0],fPhotonData,nphotons)

    
@cython.boundscheck(False)    
def MakePhotonMessage(chromaData):
    photons = GenScintPhotons(chromaData)
    events = sim.simulate(photons, keep_photons_end=True, max_steps=2000)
    stime = time.clock()
    cdef float const1 = float((2*(np.pi)*(6.582*(10**-16))*(299792458.0)))
    cdef float const2 = (4.135667516 * (10**-21))
    cdef int n, f
    cdef np.ndarray[DTYPEINT_t,ndim = 1] channelhit	
    cdef np.ndarray[unsigned int,ndim = 1] detected_photons

    phits = PhotonHits()
    for ev in events:
        detected_photons = ev.photons_end.flags[:] & <DTYPEUINT16_t>chroma.event.SURFACE_DETECT
        channelhit = np.zeros(len(detected_photons),dtype = DTYPEINT)
        channelhit[:] = det.solid_id_to_channel_index[ det.solid_id[ev.photons_end.last_hit_triangles[:] ] ]
        phits.count = int(np.count_nonzero(detected_photons))
        for n,f in enumerate(detected_photons):
            if f==0:
                continue
            else:
                #print "hit detID:",channelhit[n]," pos=",ev.photons_end.pos[n,:]," time=",ev.photons_end.t[n]
                pass
                # phits = encode_data(PhotonHits, [{'PMTID': int(channelhit[n]), 'Time': float(ev.photons_end.t[n]), 'KineticEnergy': (const1 / float(ev.photons_end.wavelengths[n])), 'posX': (float(ev.photons_end.pos[n,0])), 'posY': float(ev.photons_end.pos[n,1]), 'posZ' : float(ev.photons_end.pos[n,2]), 'momX' : (const2 /float((ev.photons_end.wavelengths[n])) * float(ev.photons_end.dir[n,0])), 'momY' : (const2 /float((ev.photons_end.wavelengths[n])) * float(ev.photons_end.dir[n,1])), 'momZ' : (const2 /float((ev.photons_end.wavelengths[n])) * float(ev.photons_end.dir[n,2])),'polX' : float(ev.photons_end.pol[n,0]), 'polY' : float(ev.photons_end.pol[n,1]), 'polZ' : float(ev.photons_end.pol[n,2]), 'origin' : photonHit_pb2.Photon.CHROMA}])
            #aphoton = phits.photon.add()
            #aphoton.PMTID = int(channelhit[n])
            #aphoton.Time = float(ev.photons_end.t[n])
            #aphoton.KineticEnergy = (const1/float((ev.photons_end.wavelengths[n])))
            #aphoton.posX = float(ev.photons_end.pos[n,0])
            #aphoton.posY = float(ev.photons_end.pos[n,1])
            #aphoton.posZ = float(ev.photons_end.pos[n,2])
            # px = |p|*cos(theta) = (h / lambda)*(<u,v> / |u||v|) = (h / lambda)*(u1 / |u|), etc.
            #turns out we don't need to to this... px = |p|*phat = (h / lambda) * (dir[n,0]...etc.
            # aphoton.momX = (const2 /float((ev.photons_end.wavelengths[n]))) * float((ev.photons_end.dir[n,0]))
            # aphoton.momY = (const2 /float((ev.photons_end.wavelengths[n]))) * float((ev.photons_end.dir[n,1]))
            # aphoton.momZ = (const2 /float((ev.photons_end.wavelengths[n]))) * float((ev.photons_end.dir[n,2]))
            # aphoton.polX = float(ev.photons_end.pol[n,0])
            # aphoton.polY = float(ev.photons_end.pol[n,1])
            # aphoton.polZ = float(ev.photons_end.pol[n,2])
            # aphoton.origin = photonHit_pb2.Photon.CHROMA 
    etime = time.clock()
    print "TIME TO MAKE MESSAGE: ",(etime-stime)
    return phits

@cython.boundscheck(False)
def GenScintPhotons(protoString):
    stime = time.clock()
    cdef int nsphotons,stepPhotons,i,j
    cdef np.ndarray[DTYPEFLOAT32_t,ndim = 2] pos, pol
    cdef np.ndarray[DTYPEFLOAT32_t,ndim = 1] wavelengths, t
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
    phi = np.random.uniform(0,2.0*np.pi, nsphotons).astype(np.float32)
    dir = np.array( zip( np.sqrt(1-dcos[:]*dcos[:])*np.cos(dphi[:]), np.sqrt(1-dcos[:]*dcos[:])*np.sin(dphi[:]), dcos[:] ), dtype=np.float32 )
    pol[:,0] = np.cos(phi)
    pol[:,1] = np.sin(phi)
    stepPhotons = 0
    for i,sData in enumerate(protoString.stepdata):
        #instead of appending to array every loop, the full size (nsphotons x 3) is allocated to begin, then 
        #values are filled properly by incrementing stepPhotons.
        for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
            pos[j,0] = np.random.uniform(sData.step_start_x,sData.step_end_x)
            pos[j,1] = np.random.uniform(sData.step_start_y,sData.step_end_y)
            pos[j,2] = np.random.uniform(sData.step_start_z,sData.step_end_z)
        #moved pol outside of the loop. saved ~3 seconds in event loop time. 
        # for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
        #     pol[j,0] = np.random.uniform(0,((1/3.0)**.5))
        #     pol[j,1] = np.random.uniform(0,((1/3.0)**.5))
        #     pol[j,2] = ((1 - pol[j,0]**2 - pol[j,1]**2)**.5)
        for j in xrange(stepPhotons, (stepPhotons+sData.nphotons)):
            t[j] = (np.random.exponential(1/45.0) + (sData.step_end_t-sData.step_start_t))
        stepPhotons += sData.nphotons
    etime = time.clock()
    print "TIME TO GEN PHOTONS: ",(etime-stime)
    return Photons(pos = pos, pol = pol, t = t, dir = dir, wavelengths = wavelengths)
