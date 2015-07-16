#include "photonHit.pb.h"
#include <cmath>
#include <zmq.hpp>
#include <string>

const float const1 = (2.0 * 3.1415926535)*(6.582*(pow(10.0,-16)))*(299792458.0);
const float const2 = (4.135667516 * (pow(10.0,-21)));

void C_MessagePack(int* PMTArr, float* TimeArr, float* WaveArr, float* PosArr, float* DirArr, float* PolArr, int nphotons){
  hitPhotons::PhotonHits fPhotonData;
  hitPhotons::Photon* aphoton;
  int i, j, index;
  index = 0;
  for (i = 0; i < nphotons; i++){
    aphoton = fPhotonData.add_photon();
    aphoton->set_pmtid(PMTArr[index]);
    aphoton->set_time(TimeArr[index]);
    aphoton->set_kineticenergy(const1 / (WaveArr[index]));
    ////////////////////////////
    //set origin to chroma here.
    ////////////////////////////
    for (j = 0; j < 3; j++){
      aphoton->set_posx(PosArr[index]);
      aphoton->set_posy(PosArr[index]);
      aphoton->set_posz(PosArr[index]);
      aphoton->set_momx(const2 / ((WaveArr[index]) * (DirArr[index])));
      aphoton->set_momy(const2 / ((WaveArr[index]) * (DirArr[index])));
      aphoton->set_momz(const2 / ((WaveArr[index]) * (DirArr[index])));
      aphoton->set_polx(PolArr[index]);
      aphoton->set_poly(PolArr[index]);
      aphoton->set_polz(PolArr[index]);
      index++;
    }
  }
}

//  Sends string as 0MQ string
static bool
s_send (zmq::socket_t & socket, const std::string & string) {

    zmq::message_t message(string.size());
    memcpy (message.data(), string.data(), string.size());

    bool rc = socket.send (message);
    return (rc);
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

void shipBack(hitPhotons::PhotonHits fPhotonData){
  zmq::context_t* context = new zmq::context_t(1);
  // want to connect to the server endpoint here.
  zmq::socket_t* client = new zmq::socket_t (*context, ZMQ_REP);
  client->connect("tcp:://localhost:5556");
  
  std::string str_msg;
  fPhotonData.SerializeToString(&str_msg);
  s_send(*client,str_msg);
  s_recv(*client);

  delete client;
  delete context;
  
}

