#include "photonHit.pb.h"
#include <cmath>
#include <zmq.hpp>
#include <string>

void C_MessagePack(int* PMTArr, float* TimeArr, float* WaveArr, float* PosArr, float* DirArr, float* PolArr, int nphotons);
//  Sends string as 0MQ string
bool s_send (zmq::socket_t & socket, const std::string & string);

//  Receive 0MQ string from socket and convert into C string
//  Caller must free returned string. Returns NULL if the context
//  is being terminated.
char * s_recv (void *socket);

void shipBack();

std::string returnPhits();
