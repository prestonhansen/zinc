//
//
#include "zhelpers.hpp"
#include <string>

static zmq::socket_t * s_client_socket (zmq::context_t & context) {
  zmq::socket_t * client = new zmq::socket_t (context, ZMQ_REP);
  client->connect ("tcp://localhost:5556");
  return client;
} 
int main () {
  zmq::context_t context(1);
 
  zmq::socket_t *client = s_client_socket (context);

  while (true) {
    std::string msg = s_recv (*client);
    if (msg == "go"){
      s_send (*client, "");
    }
    bool expect_reply = true;
    while (expect_reply) {
      std::string data = s_recv (*client);
      std::cout << data << "\n" << "sending back";
      s_send (*client, data);
      expect_reply = false;
      //can expand this loop to implement some cheap reliability
   }
  }
  delete client;
  return 0;
}


