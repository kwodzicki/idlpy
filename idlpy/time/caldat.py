from datetime import datetime

import numpy as np

"""
Copyright (c)  Harris Geospatial Solutions, Inc. All
      rights reserved. Unauthorized reproduction is prohibited.



NAME:
      CALDAT

PURPOSE:
      Return the calendar date and time given julian date.
      This is the inverse of the function JULDAY.
CATEGORY:
      Misc.

CALLING SEQUENCE:
      CALDAT, Julian, Month, Day, Year, Hour, Minute, Second
      See also: julday, the inverse of this function.

INPUTS:
      JULIAN contains the Julian Day Number (which begins at noon) of the
      specified calendar date.  It should be a long integer.
OUTPUTS:
      (Trailing parameters may be omitted if not required.)
      MONTH:   Number of the desired month (1 = January, ..., 12 = December).

      DAY:  Number of day of the month.

      YEAR: Number of the desired year.

      HOUR: Hour of the day
      Minute: Minute of the day
      Second: Second (and fractions) of the day.

COMMON BLOCKS:
      None.

SIDE EFFECTS:
      None.

RESTRICTIONS:
      Accuracy using IEEE double precision numbers is approximately
      1/10000th of a second.

MODIFICATION HISTORY:
      Translated from "Numerical Recipies in C", by William H. Press,
      Brian P. Flannery, Saul A. Teukolsky, and William T. Vetterling.
      Cambridge University Press, 1988 (second printing).

      DMS, July 1992.
      DMS, April 1996, Added HOUR, MINUTE and SECOND keyword
      AB, 7 December 1997, Generalized to handle array input.
      AB, 3 January 2000, Make seconds output as DOUBLE in array output.
CT, Nov 2006: For Hour/Min/Sec, tweak the input to make sure hours
      and minutes are correct. Restrict hours to 0-23 & min to 0-59.
CT, June 2012: Add undocumented PROLEPTIC_GREGORIAN, used by JUL2GREG.
    Also rewrote the algorithm using integer arithmetic, for speed.

"""

MIN_JULIAN = -31776
MAX_JULIAN = 1827933925

def caldat(julian, prolepticGregorian = False):

  minn = min(julian)
  maxx = max(julian)

  if (minn < MIN_JULIAN) or (maxx > MAX_JULIAN):
     raise Exception('Value of Julian date is out of allowed range.')

  igreg   = 2299161    #Beginning of Gregorian calendar
  isFloat = isinstance(julian, float)
  if isinstance(julian, np.ndarray):
    isFloat = isFloat or (julian.dtype == np.float) 
    isFloat = isFloat or (julian.dtype == np.float32)
    isFloat = isFloat or (julian.dtype == np.float64)
  if isFloat: 
    julLong = np.floor(julian + 0.5).astype( np.int32 ) 
  else:
     julLong = julian
  minJul = min(julLong)
  
  jShift = julLong + 32082  # shift back to 4800 BC
 
  if minJul >= igreg or prolepticgregorian:
    jShift -= 38
    g400    = jShift // 146097
    deltaG  = jShift % 146097
    c100    = ((deltaG // 36524 + 1)*3) // 4
    deltaC  = deltaG - c100*36524
    year    = g400*400 + c100*100

  else:
    n      = len(jShift)
    deltaC = jShift
    year   = np.zeros(n, dtype=np.int32) if n > 1 else 0

    gregChange = np.where(julLong >= igreg)
    ngreg      = gregChange[0].size

    if (ngreg > 0):
      js     = jShift[gregChange] - 38
      g400   = js // 146097
      deltaG = js % 146097
      c100   = ((deltaG // 36524 + 1)*3) // 4
      deltaC[gregChange] = deltaG - c100*36524
      year[gregChange]   = g400*400 + c100*100
    

  b4     = deltaC // 1461
  deltaB = deltaC % 1461
  a      = (deltaB // 365 + 1)*3 // 4
  deltaA = deltaB - 365*a
    
  year += b4*4 + a
  month = (5*deltaA + 308) // 153
  day   = deltaA - ((month + 2)*153) // 5 + 123

  year = year - 4800 + month // 12
  isBC = (year <= 0)
  if np.sum(isBC == 0) != 0: year -= isBC

  month = (month % 12) + 1


# see if we need to do hours, minutes, seconds
  fraction  = julian + 0.5 - julLong
  eps       = np.clip(1.0e-12*abs(julLong), 1.0e-12, None)
  hour      = np.clip(np.floor(fraction * 24.0 + eps), 0, 23).astype(int)
  fraction -= hour/24.0
  minute    = np.clip( np.floor(fraction*1440.0 + eps), 0, 59).astype(int)
  second    = np.clip( (fraction - minute/1440.0)*86400.0, 0, None)
  micro     = ((second - np.floor(second)) * 1.0e6).astype(int)
  second    = second.astype(int)

# if julian is an array, reform all output to correct dimensions
  if julian.ndim > 0:
    dimensions = julian.shape
    month      = month.reshape( dimensions)
    day        = day.reshape(   dimensions)
    year       = year.reshape(  dimensions)
    hour       = hour.reshape(  dimensions)
    minute     = minute.reshape(dimensions)
    second     = second.reshape(dimensions)
    micro      = micro.reshape( dimensions)
    dates      = np.empty( dimensions, dtype = object )
    for i in range( julian.size ):
      dates.flat[i] = datetime( year.flat[i], month.flat[i],  day.flat[i],
                                hour.flat[i], minute.flat[i], second.flat[i], 
                                micro.flat[i] )
  else:
    dates = datetime( year, month, day, hour, minute, second, micro)

  return dates
  return year, month, day, hour, minute, second
