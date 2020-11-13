import numpy
from datetime import datetime

"""
Calculate the Julian Day Number for a given month, day, and year.

This is the inverse of the library function CALDAT.
See also caldat, the inverse of this function.

 CATEGORY:
	Misc.

 CALLING SEQUENCE:
	Result = JULDAY([[[[Month, Day, Year], Hour], Minute], Second])

 INPUTS:
	MONTH:	Number of the desired month (1 = January, ..., 12 = December).

	DAY:	Number of day of the month.

	YEAR:	Number of the desired year.Year parameters must be valid
               values from the civil calendar.  Years B.C.E. are represented
               as negative integers.  Years in the common era are represented
               as positive integers.  In particular, note that there is no
               year 0 in the civil calendar.  1 B.C.E. (-1) is followed by
               1 C.E. (1).

	HOUR:	Number of the hour of the day.

	MINUTE:	Number of the minute of the hour.

	SECOND:	Number of the second of the minute.

   Note: Month, Day, Year, Hour, Minute, and Second can all be arrays.
         The Result will have the same dimensions as the smallest array, or
         will be a scalar if all arguments are scalars.

 OPTIONAL INPUT PARAMETERS:
	Hour, Minute, Second = optional time of day.

 OUTPUTS:
	JULDAY returns the Julian Day Number (which begins at noon) of the
	specified calendar date.  If Hour, Minute, and Second are not specified,
	then the result will be a long integer, otherwise the result is a
	double precision floating point number.

 COMMON BLOCKS:
	None.

 SIDE EFFECTS:
	None.

 RESTRICTIONS:
	Accuracy using IEEE double precision numbers is approximately
   1/10000th of a second, with higher accuracy for smaller (earlier)
   Julian dates.

 MODIFICATION HISTORY:
	Translated from "Numerical Recipies in C", by William H. Press,
	Brian P. Flannery, Saul A. Teukolsky, and William T. Vetterling.
	Cambridge University Press, 1988 (second printing).

	AB, September, 1988
	DMS, April, 1995, Added time of day.
 CT, April 2000, Now accepts vectors or scalars.
 CT, June 2012: Add undocumented PROLEPTIC_GREGORIAN, used by GREG2JUL.
     Also rewrote the algorithm using integer arithmetic, for speed.

"""

GREG         = 2299171  # incorrect Julian day for Oct. 25, 1582
MIN_CALENDAR =   -4801
MAX_CALENDAR = 5000000

def julday( *args, proleptic_gregorian=False):
  np = len(args)
  if np == 0:
    np     = 6
    date   = datetime.now()
    year   = [date.year]
    month  = [date.month]
    day    = [date.day] 
    hour   = [date.hour]
    minute = [date.minute]
    second = [date.second + date.microsecond/1.0e6]
  elif np == 1 and isinstance(args[0], datetime):
    np     = 6
    year   = [args[0].year]
    month  = [args[0].month]
    day    = [args[0].day] 
    hour   = [args[0].hour]
    minute = [args[0].minute]
    second = [args[0].second + args[0].microsecond/1.0e6]
  elif np < 3:
    raise Exception('Incorrect number of inputs') 
  else:
    args = [arg if isinstance(arg, (list, tuple,)) else [arg] for arg in args]
    if np == 3:
      args += [ [12], [0], [0] ]
    elif np == 4:
      args += [ [0], [0] ]
    elif np == 5:
      args += [ [0] ]
    year   = args[0] 
    month  = args[1]
    day    = args[2]
    hour   = args[3] 
    minute = args[4]
    second = args[5]
  year   = numpy.asarray(year,   dtype=numpy.int32) 
  month  = numpy.asarray(month,  dtype=numpy.int32)
  day    = numpy.asarray(day,    dtype=numpy.int32)
  hour   = numpy.asarray(hour,   dtype=numpy.int32) 
  minute = numpy.asarray(minute, dtype=numpy.int32)
  second = numpy.asarray(second, dtype=numpy.float32)

  # Gregorian Calander was adopted on Oct. 15, 1582
  # skipping from Oct. 4, 1582 to Oct. 15, 1582

  # Find the dimensions of the Result:
  #  1. Find all of the input arguments that are arrays (ignore scalars)
  #  2. Out of the arrays, find the smallest number of elements
  #  3. Find the dimensions of the smallest array

  # Step 1: find all array arguments
  nDims = numpy.array( 
         [month.ndim,  day.ndim,
  	  year.ndim,   hour.ndim,
  	  minute.ndim, second.ndim]
  )
  arrays = numpy.where(nDims > 1)[0]

  nJulian    = 1    # assume everything is a scalar
  julianDims = None
  if arrays.size > 0:
    # Step 2: find the smallest number of elements
    nElement = numpy.array(
           [month.size,  day.size,
  	    year.size,   hour.size, 
  	    minute.size, second.size]
    )
    nJulian  = nElement[arrays].min()
    whichVar = numpy.argmin( nElement[arrays] )
    # step 3: find dimensions of the smallest array
    if arrays[whichVar] == 0:
      julianDims = month.shape
    elif arrays[whichVar] == 1:
      julianDims = day.shape
    elif arrays[whichVar] == 2:
      julianDims = year.shape
    elif arrays[whichVar] == 3:
      julianDims = hour.shape
    elif arrays[whichVar] == 4:
      julianDims = minute.shape
    elif arrays[whichVar] == 5:
      julianDims = second.shape

  d_Second = 0.0  # defaults
  d_Minute = 0.0
  d_Hour   = 0.0
  L_MONTH  = month.flatten()[0:nJulian] if month.ndim > 0 else month
  L_DAY    = day.flatten()[  0:nJulian] if day.ndim   > 0 else day
  L_YEAR   = year.flatten()[ 0:nJulian] if year.ndim > 0 else year
  # convert all Arguments to appropriate array size & type
  if np > 3:
    d_Hour = hour.flatten()[0:nJulian] if hour.ndim > 0 else hour
    if np > 4:
      d_Minute = minute.flatten()[0:nJulian] if minute.ndim > 0 else minute
      if np > 5:
        d_Second = second.flatten()[0:nJulian] if second.ndim > 0 else nsecond

  minn = min(L_YEAR)
  maxx = max(L_YEAR)
  if (minn < MIN_CALENDAR) or (maxx > MAX_CALENDAR):
    raise Exception( 'Value of Julian date is out of allowed range.' )
  if (max(L_YEAR == 0) != 0):
    raise Exception('There is no year zero in the civil calendar.' )


  bc        = (L_YEAR < 0)
  L_YEAR    =  L_YEAR + bc
  inJanFeb  = (L_MONTH <= 2)
  JY        = L_YEAR - inJanFeb + 4800
  JM        = L_MONTH + 12*inJanFeb - 3

  JUL = 365*JY + JY//4 + (153*JM+2)//5 + L_DAY - 32083

  # Test whether to change to Gregorian Calendar.
  # For the Gregorian calendar, *after 1582*, if the year ends in a 00,
  # then it is not a leap year, unless it is also divisible by 400.
  # ;
  # The proleptic Gregorian extends the Gregorian calendar backwards to dates
  # preceeding its introduction on 15 Oct 1582. For 15 Oct 1582 or later,
  # the Julian Day Number will be equal regardless of whether the proleptic
  # Gregorian is used or not.
  if min(JUL) >= GREG or proleptic_gregorian:
    JUL += 38 - JY//100 + JY//400
  else:
    gregChange = JUL >= GREG
    JY = JY[gregChange]
    JUL[gregChange] += 38 - JY//100 + JY//400

  # hour,minute,second?
  if np > 3: # yes, compute the fractional Julian date
  # Add a small offset so we get the hours, minutes, & seconds back correctly
  # if we convert the Julian dates back. This offset is proportional to the
  # Julian date, so small dates (a long, long time ago) will be "more" accurate.
    eps = numpy.finfo(numpy.float64).eps
    eps = numpy.clip( eps*abs(JUL), eps, None)
  # For Hours, divide by 24, then subtract 0.5, in case we have unsigned ints.
    JUL = JUL + ( (d_Hour/24.0 - 0.5) + \
        d_Minute/1440.0 + d_Second/86400.0 + eps )
  
  # check to see if we need to reform vector to array of correct dimensions
  if julianDims:
    JUL = JUL.reshape(julianDims)
  return JUL

def julday_no_leap(month, day, year):
  ileapday = numpy.where( (month == 2) & (data == 29) )
  if ileapday[0].size > 0: raise Exception('February 29 not permitted in julday_no_leap')

  if numpy.sum(month < 1) > 0 or numpy.sum(month > 12) > 0:
    raise Exception( 'Month out of rnage in julday_no_leap' )
  if numpy.sum(day   < 1) > 0 or numpy.sum(day   > 31) > 0:
    raise Exception( 'Day out of range in julday_no_leap')

  return julday(month, day, 2001) + 365*(year - 2001)

