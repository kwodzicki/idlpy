from datetime import datetime, timedelta

import numpy as np

from .julday import julday
from .caldat import caldat

def julday2datetime( julday, seconds ):
  """
  Convert Astronomical Julian day and seconds into python datetime

  Arguments:
    julday (int,float)  : Astronomical Julian day
    seconds (int,float) : Seconds of the day

  Keyword arguments:
    None.

  Returns:
    datetime : Date of time

  """

  return caldat( julday ) + timedelta( seconds = seconds )


def datetime2julday( date ):
  """
  Convert python datetime into Astronomical Julian day and seconds

  Arguments:
    date : Date(s) to convert

  Keyword arguments:
    None.

  Returns:
    tuple : ( julday, seconds)

  """
  if not isinstance(date, np.ndarray):
    date = np.atleast_1d(date)

  julian  = np.empty( date.shape, dtype=np.int32 )
  seconds = np.empty( date.shape, dtype=np.int32 )
  for i in range(date.size):
    t0  = datetime(date[i].year, date[i].month, date[i].day)
    
    seconds[i] = (date[i] - t0).total_seconds()
    julian[ i] = julday(date[i].year, date[i].month, date[i].day)
    
  return julian, seconds 
