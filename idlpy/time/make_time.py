import numpy as np

from .julday import julday as julianday
from .julday import julday_no_leap
from .jtime import JTime

def make_time( *args, julday = None, seconds = None, no_leap = False):
  """
  This makes a Julian day plus seconds from a date and time, or optionally from arrays containing the Julian days and seconds.

  Example:
    date = make_time([year, [month, [day, [hour, [minute, [second]]]]]])

  INPUT:
  		year   : Optional calendar year
  		month  : Optional month (1 to 12)
  		day    : Optional day of the month (1 to 28, 30, or 31)
  		hour   : Optional hour (0 to 23)
  		minute : Optional minute (0 to 59)
  		second : Optional second (0 to 59)
  OUTPUT:
       t    : structure {jtime, jday: 0L, seconds: 0L} 
              containing the date as Julian day and seconds from midnight
  KEYWORDS:
       JULDAY  : scalar or array containing Julian day numbers
  		SECONDS : scalar or array containing time of day in seconds
  MODIFICATION HISTORY:
       KPB, April, 1999.
       Updated to include NO_LEAP option, KPB, March, 2001.
  		Cameron Homeyer, 2011-12. Vectorized.
  """

  nt = 1
  if julday is not None:
    julday = np.asarray( julday )
    nt     = julday.shape
  elif len(args) > 0:
    year = np.asarray( args[0] )
    nt   = year.shape

  if seconds is not None: seconds = np.asarray( seconds )
 
  time      = np.empty( nt, dtype = object )
  time.flat = [JTime( no_leap = no_leap ) for _ in time.flat] 
      
  if julday is not None:
    ibad = np.where( (seconds < 0) | (seconds >= 86400) )			        # Check seconds
    if ibad[0].size > 0: raise Exception( 'Seconds out of range in MAKE_TIME' )
    for i in range(time.size):
      time.flat[i].jday    = julday.flat[i]
      time.flat[i].seconds = seconds.flat[i]
  else:
    second = np.zeros(nt) if len(args) < 6 else args[5]					# Default value for second
    minute = np.zeros(nt) if len(args) < 5 else args[4]					# Default value for minute
    hour   = np.zeros(nt) if len(args) < 4 else args[3]					# Default value for hour
    day    = np.ones( nt) if len(args) < 3 else args[2]					# Default value for day
    month  = np.ones( nt) if len(args) < 2 else args[1] 				# Default value for month
    year   = np.ones( nt) if len(args) < 1 else args[0]					# Default value for year

    if not isinstance(year, (list,tuple,np.ndarray)):
      year = np.asarray( [year] )
    if not isinstance(month, (list,tuple,np.ndarray)):
      month = np.asarray( [month] )
    if not isinstance(day, (list,tuple,np.ndarray)):
      day = np.asarray( [day] )
    if not isinstance(year, (list,tuple,np.ndarray)):
      hour = np.asarray( [hour] )
    if not isinstance(minute, (list,tuple,np.ndarray)):
      minute = np.asarray( [minute] )
    if not isinstance(second, (list,tuple,np.ndarray)):
      second = np.asarray( [second] )

    if np.sum(month  <  1) > 0 or np.sum(month  > 12) > 0:
      raise Exception( 'Month out of range in MAKE_TIME.' ) # Check month range
    if np.sum(day    <  1) > 0 or np.sum(day    > 31) > 0:
      raise Exception( 'Day out of range in MAKE_TIME.' )			#Check day range
    if np.sum(minute <  0) > 0 or np.sum(minute > 59) > 0:
      raise Exception( 'Minute out of range in MAKE_TIME.' )			#Check minute range
    if np.sum(second <  0) > 0 or np.sum(second > 59) > 0:
      raise Exception( 'Second out of range in MAKE_TIME.' )			#Check second range

    if no_leap:
      for i in range( time.size ):
        time.flat[i].jday = julday_no_leap(month, day, year) 				# Compute Julian day
    else:
      for i in range( time.size ):
         time.flat[i].jday = julianday(month, day, year)					# Compute NO_LEAP Julian day

    for i in range( time.size ): 
      time.flat[i].seconds = 3600*hour[i] + 60*minute[i] + second[i]				# Compute seconds

  if len(time) == 1:
    return time[0]
  else:
    return time

