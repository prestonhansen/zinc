from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy

setup(
    name = "message_pack_cpp",
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("message_pack_cpp",
                             sources=["ChromaSimCython.pyx","photonMessage.cpp","photonHit.pb.cc"],
                             include_dirs=[numpy.get_include(),"/home/nudot/protobuf/include/","/home/nudot/RATChromaServer/"],
                             library_dirs=['/home/nudot/protobuf/lib'],
                             libraries=['protobuf'],
                             language="c++",
                         )],
    
    )
