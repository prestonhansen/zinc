# zinc: a ZMQ Interface for Chroma
##09/02/15##
Reorganized the repo in preparation for continued development for the Fall 2015 semester. No functionality has changed, and I have postponed development of a flatbuffers implementation for the time being.
##07/07/15##
Renamed the repo to zinc, and condensed all functionality into zinc.py. as of right now zinc.py specifically interfaces with the RAT/Chroma setup that I'm working with, but eventually it will be written generally such that anyone cloning the repo can easily configure it for their project.
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

#USAGE#

UPDATE 07/07/15: simply run zinc.py, a rat macro, and ChromaPoller.py in your chroma environment and magic will happen.

UPDATE 09/02/15: as of right now none of the directories are implemented in a clean way. Once the proto file has been built, the cython library files must be built by running setup.py (currently configured for nudot, will need modification for a different setup), and ChromaPoller should be run from the directory that the chroma environment is in.
Other info: Port selection (as of now): Zinc binds to 5554, 5555, and 5556. 5554: Queuer interfaces with RAT. 5555: Queuer Interfaces with the Server layer of zinc. 5556: Server Interfaces with Chroma.
