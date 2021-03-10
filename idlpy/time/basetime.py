import numpy 

from .caldat import caldat
from .julday import julday

class Basetime():
  SEC_PER_MIN  =    60
  SEC_PER_HOUR =  3600
  SEC_PER_DAY  = 86400

  def __init__(self, *args, caltype = 'CALDAT'):
    self.args    = numpy.atleast_1d( args ) 
    self.caltype = caltype

  def make_date(self, now = False, utc = False, no_leap = False):
    pass
    #if now:
     

  def time_to_date(self):
    if numpy.sum( (self.args[1,:] < 0) | (self.args[1,:] > self.SEC_PERDAY) ) > 0:
      raise Exception( 'Seconds out of range in {}'.format(__name__) )

    if self.caltype == 'JTIME':
      date    = caldat(self.args[0,:])
      no_leap = False
    elif self.caltype == 'JTIME_NO_LEAP':
      date    = caldat_no_leap(self.args[0,:])
      no_leap = True

    hour   = self.args[1,:] // self.SEC_PER_HOUR
    minute = (self.args[1,:] - self.SEC_PER_HOUR) // self.SEC_PER_MINUTE
    second = self.args[1,:] - self.SEC_PER_HOUR*hour - self.SEC_PER_MINUTE * minute

    return 
  def make_iso_date_string(self, precision = None, compact=False, utc=False, no_t = False):
    if self.caltype in ('JTIME' , 'JTIME_NO_LEAP'):
      date = self.time_to_date()
  
