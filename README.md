# RATChromaServer


##06/24/15##
some files in the repo are deprecated. 

Server.py is deprecated, since it was used as a dummy prototype for what newServer.py does at the moment. 

ChromaClient and RATclient were both dummy clients, and are also deprecated. 

zmq.hpp and zhelpers.hpp are both used by these scripts (and by ratpac-chroma), but they are included in
both repositories for clarity's sake.

at the moment, the order in which the scripts are run matters. this will be fixed once the model is actually
implemented. At some point, the networking layers will become flexible in regards to when one is opened or closed. 
Further, there will be reliability features built into the networking layers that allow clients/servers to 
disconnect or die without breaking everything else. 


---------------USAGE---------------
As of now, the order is queue.py/server.py -> server.py/queue.py -> ChromaPoller.py -> run RAT.
