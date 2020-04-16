from .interpolate import interpolate
from .randomu import randomu
from .julday import julday

class Structure(object):
  def __init__(self, **kwargs):
    for key, val in kwargs.items():
      self[key] = val
  def __getitem__(self, key):
    return self.__dict__[key]
  def __setitem__(self, key, val):
    self.__dict__[key] = val
  def __contains__(self, key):
    return key in self.__dict__
  def keys(self):
    return self.__dict__.keys()
