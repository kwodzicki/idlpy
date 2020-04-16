import os, shutil, importlib
from setuptools import setup, convert_path, find_packages, Extension
from setuptools.command.install import install
try:
  from Cython.Build import cythonize, build_ext
except:
  raise Exception("Cython is not installed. Try installing using 'pip3 install cython'")

try:
  import numpy
except:
  raise Exception("numpy is not installed. Try installing using 'pip3 install numpy'")

#try:
#  import yaml
#except:
#  raise Exception("pyYAML is not installed. Try installing using 'pip3 install pyYAML'")
  
NAME = 'idlpy'
DESC = 'Package containing python ports of some useful IDL functions and procedures'
 

main_ns  = {}
ver_path = convert_path("{}/version.py".format(NAME))
with open(ver_path) as ver_file:
  exec(ver_file.read(), main_ns);

exts = [
  Extension( '{}.interpolate'.format(NAME),
             sources            = ['{}/interpolate.pyx'.format(NAME)],
             extra_compile_args = ['-fopenmp'],
             extra_link_args    = ['-lomp']
  )
]

setup(
  name                 = NAME,
  description          = DESC,
  url                  = "",
  author               = "",
  author_email         = "",
  version              = main_ns['__version__'],
  packages             = find_packages(),
  install_requires     = [ ],
  ext_modules          = cythonize( exts ),
  include_dirs         = [numpy.get_include()],
  cmdclass             = {'build_ext' : build_ext},
  scripts              = [],
  zip_safe             = False,
)
