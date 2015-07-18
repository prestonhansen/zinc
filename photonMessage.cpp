#include "photonMessage.hh"
#include <cmath>
#include <string>
#include <iostream>

namespace Message_Pack{
  const float const1 = (2.0 * 3.1415926535)*(6.582*(pow(10.0,-16)))*(299792458.0);
  const float const2 = (4.135667516 * (pow(10.0,-21)));
  hitPhotons::PhotonHits fPhotonData;
  zmq::context_t* context;
  zmq::socket_t* client;
  void C_MessagePack(int* PMTArr, float* TimeArr, float* WaveArr, float* PosArr, float* DirArr, float* PolArr, int nphotons){
    hitPhotons::Photon* aphoton;
    int i, i_index, j_index;
    i_index = 0;
    j_index = 0;
    std::cout << "started message pack\n";
    for (i = 0; i < nphotons; i++){
      if (PMTArr[i_index] >=0){
        aphoton = fPhotonData.add_photon();
        aphoton->set_pmtid(PMTArr[i_index]);
        aphoton->set_time(TimeArr[i_index]);
        aphoton->set_kineticenergy(const1 / (WaveArr[i_index]));
        ////////////////////////////
        //set origin to chroma here.
        ////////////////////////////
        aphoton->set_posx(PosArr[j_index]);
        aphoton->set_posy(PosArr[j_index + 1]);
        aphoton->set_posz(PosArr[j_index + 2]);
        aphoton->set_momx(const2 / ((WaveArr[i_index]) * (DirArr[j_index])));
        aphoton->set_momy(const2 / ((WaveArr[i_index]) * (DirArr[j_index + 1])));
        aphoton->set_momz(const2 / ((WaveArr[i_index]) * (DirArr[j_index + 2])));
        aphoton->set_polx(PolArr[j_index]);
        aphoton->set_poly(PolArr[j_index + 1]);
        aphoton->set_polz(PolArr[j_index + 2]);
      
        j_index+=3;
        i_index++;
      }
      else{
        i_index++;
        j_index+=3;
      }
    }
    //std::cout << fPhotonData.DebugString();
    std::cout <<"finished\n";
  }
  
  //  Sends string as 0MQ string
  bool
  s_send (zmq::socket_t & socket, const std::string & string) {
  
    zmq::message_t message(string.size());
    memcpy (message.data(), string.data(), string.size());
  
    bool rc = socket.send (message);
    return (rc);
  }
  
  //  Receive 0MQ string from socket and convert into C string
  //  Caller must free returned string. Returns NULL if the context
  //  is being terminated.
  char *
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
  void shipBack(){
    std::cout << "!!!!!!!!!!!!!!!!!! SHIP BACK START !!!!!!!!!!!\n";
    context = new zmq::context_t(1);
    // want to connect to the server endpoint here.
    client = new zmq::socket_t (*context, ZMQ_REP);
    client->connect("tcp://localhost:5557");
    std::cout << "\nconnected\n"; 
    std::string str_msg;
    fPhotonData.SerializeToString(&str_msg);
    s_recv(*client);
    s_send(*client,str_msg);
    std::cout << "sent\n";
    fPhotonData.Clear();
  }
  std::string returnPhits(){
    std::string phits;
    fPhotonData.SerializeToString(&phits);
    return phits;
  }
  void killSocket(){
    delete client;
    delete context;
  }

}
