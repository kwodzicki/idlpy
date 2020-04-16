from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize, build_ext
import numpy


exts = [Extension( name='interpolate',
        sources=['interpolate.pyx'],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-lomp']
)]

setup(
    name = 'interpolate',
    ext_modules = cythonize( exts),
    include_dirs = [numpy.get_include()],
    cmdclass={'build_ext' : build_ext}
)
