#include "photonHit.pb.h"
#include <cmath>
#include "zmq.hpp"

const float const1 = (2.0 * 3.1415926535)*(6.582*(pow(10.0,-16)))*(299792458.0);
const float const2 = (4.135667516 * (pow(10.0,-21)));

void C_MessagePack(int* PMTArr, float* TimeArr, float* WaveArr, float* PosArr, float* DirArr, float* PolArr, int nphotons){
  hitPhotons::PhotonHits fPhotonData;
  int i;
  for (i = 0; i < nphotons; i ++){
    aphoton = fPhotonData.add_photon();
    aphoton->set_pmtid((*PMTArr)[i]);
    aphoton->set_time((*TimeArr[i]));
    aphoton->set_kineticenergy(const1 / ((*WaveArr)[i]));
    aphoton->set_posx((*PosArr)[i,0]);
    aphoton->set_posy((*PosArr)[i,1]);
    aphoton->set_posz((*PosArr)[i,2]);
    aphoton->set_momx(const2 / (((*WaveArr)[i]) * (*DirArr[i,0])));
    aphoton->set_momy(const2 / (((*WaveArr)[i]) * (*DirArr[i,1])));
    aphoton->set_momz(const2 / (((*WaveArr)[i]) * (*DirArr[i,2])));
    aphoton->set_polx((*PolArr)[i,0]);
    aphoton->set_poly((*PolArr)[i,1]);
    aphoton->set_polz((*PolArr)[i,2]);
    ////////////////////////////
    //set origin to chroma here.
    ////////////////////////////
  }

}

void shipBack(hitPhotons::PhotonHits fPhotonData){
  context = new zmq::context_t(1);
  // want to connect to the server endpoint here.
  zmq::socket_t * client = new zmq::socket_t (zmq::context_t & context);
  client->connect("tcp:://localhost:5556");
  
  std::string str_msg;
  fPhotonData.SerializeToString(&str_msg);
  s_send(*client,str_msg);
  s_recv(*client);

  delete client;
  delete context;
  
}


static int
s_send (void *socket, char *string) {
  int size = zmq_send (socket, string, strlen (string), 0);
  return size;
}

//  Receive 0MQ string from socket and convert into C string
//  Caller must free returned string. Returns NULL if the context
//  is being terminated.
static char *
s_recv (void *socket) {
  char buffer [256];
  int size = zmq_recv (socket, buffer, 255, 0);
  if (size == -1)
    return NULL;
  if (size > 255)
    size = 255;
  buffer [size] = 0;
  return strdup (buffer);
}
