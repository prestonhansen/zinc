from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("ChromaSimCython.pyx")
)
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy


    ext_modules = [Extension("chroma_sim",
                             sources=["ChromaSimCython.pyx", "photonMessage.cpp"],
                             include_dirs=[numpy.get_include()])],

setup(
    name = "chroma_sim"
    cmdclass = {'build_ext': build_ext},
    ext_modules = cythonize(ext_modules)
    )
