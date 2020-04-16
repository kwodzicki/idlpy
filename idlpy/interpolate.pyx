from cython.parallel import prange
import numpy as np

from libc.math cimport floor
from libc.stdio cimport printf
cimport numpy as np
cimport cython

cdef int checkBound( long id, long n ) nogil:
  if id < 0:
    return 0
  elif id >= n:
    return n-1
  return id

cdef float checkIndex( float id, long n0, long n1 ) nogil:
  if id >= n1 or id < n0:
    return 0.0
  return id-n0

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def interp1d( double [:] data, float [:] xid ):
  out = np.empty( (xid.size,), dtype=np.float64 )
  cdef:
    Py_ssize_t i, x0, x1
    Py_ssize_t nx = xid.size
    long dx = data.size
    double xd 
    double [:] outView = out

  for i in range( nx ):
    x0 = checkBound( int(xid[i]), dx )
    x1 = checkBound( x0 + 1, dx )
    xd = checkIndex( xid[i], x0, x1 )
    if (xd == 0.0):
      outView[i] = data[x0]
    else: 
      outView[i] = (data[x1] - data[x0]) * xd + data[x0]

  return out

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def interp2d( double [:,::1] data, float [:] yid, float [:] xid ):
  out = np.empty( (yid.size, xid.size,), dtype=np.float64 )

  cdef:
    Py_ssize_t i, j, x0, x1, y0, y1, z0
    Py_ssize_t ny = yid.size
    Py_ssize_t nx = xid.size
    long dy = data.shape[0]
    long dx = data.shape[1]
    double xd, yd, c0, c1
    double [:,::1] outView = out

  for j in prange( ny, nogil=True ):
    y0 = checkBound( int(yid[j]), dy )
    y1 = checkBound( y0 + 1, dy)
    yd = checkIndex( yid[j], y0, y1)
    for i in range( nx ):
      x0 = checkBound( int(xid[i]), dx )
      x1 = checkBound( x0 + 1, dx )
      xd = checkIndex( xid[i], x0, x1 )
      if (xd == 0.0):
        c0 = data[y0, x0]
        c1 = data[y1, x0]
      else:
        c0 = data[y0, x0] * (1.0 - xd) + data[y0, x1] * xd
        c1 = data[y1, x0] * (1.0 - xd) + data[y1, x1] * xd
      if (yd == 0.0):
        outView[j,i] = c0 
      else:
        outView[j,i] = c0 * (1.0 - yd) + c1 * yd 

  return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def interp3d( double [:,:,::1] data, float [:] zid, float [:] yid, float [:] xid ):
  out = np.full( (zid.size, yid.size, xid.size,), np.nan, dtype=np.float64 )
  cdef:
    Py_ssize_t i, j, k, x0, x1, y0, y1, z0, z1
    Py_ssize_t nz = zid.size
    Py_ssize_t ny = yid.size
    Py_ssize_t nx = xid.size
    long dz = data.shape[0]
    long dy = data.shape[1]
    long dx = data.shape[2]
    double xd, yd, zd, c00, c01, c10, c11, c0, c1
    double [:,:,::1] outView = out

  for k in prange( nz, nogil=True ):
    z0 = checkBound( int(zid[k]), dz )
    z1 = checkBound( z0 + 1, dz )
    zd = checkIndex( zid[k], z0, z1 )
    for j in range( ny ):
      y0 = checkBound( int(yid[j]), dy )
      y1 = checkBound( y0 + 1, dy )
      yd = checkIndex( yid[j], y0, y1 )
      for i in range( nx ):
        x0  = checkBound( int(xid[i]), dx )
        x1  = checkBound( x0 + 1, dx )
        xd  = checkIndex( xid[i], x0, x1 )
        if (xd == 0.0):
          c00 = data[z0, y0, x0]
          c01 = data[z1, y0, x0]
          c10 = data[z0, y1, x0]
          c11 = data[z1, y1, x0]
        else:
          c00 = data[z0, y0, x0] * (1.0 - xd) + data[z0, y0, x1] * xd
          c01 = data[z1, y0, x0] * (1.0 - xd) + data[z1, y0, x1] * xd
          c10 = data[z0, y1, x0] * (1.0 - xd) + data[z0, y1, x1] * xd
          c11 = data[z1, y1, x0] * (1.0 - xd) + data[z1, y1, x1] * xd
        if (yd == 0.0):
          c0  = c00
          c1  = c01
        else:
          c0  = c00 * (1.0 - yd) + c10 * yd
          c1  = c01 * (1.0 - yd) + c11 * yd
        if (zd == 0.0):
          outView[k,j,i] = c0
        else:
          outView[k,j,i] = c0 * (1.0 - zd) + c1 * zd

  return out

def interpolate( data, *args, **kwargs ):
  inType = data.dtype
  if data.dtype != np.float64:
    data = data.astype( np.float64 )
  nargs = len(args)
  if nargs > 3:
    raise Exception( 'Can only perform up to trilinear interpolation' )

  args  = list( args )                                                                  # Convert args tuple to list
  for i in range( nargs ):                                                              # Iterate over all values
    if not isinstance(args[i], np.ndarray):                                             # If the argument is not a ndarray
      if not isinstance(args[i], (list, tuple,)):                                       # If arg is not list or tuple
        args[i] = (args[i],)                                                            # Convert to tuple
      args[i] = np.asarray( args[i], dtype = np.float32 )                               # Convert to ndarray
    elif args[i].dtype != np.float32:                                                   # Else, if not a 32-bit float
      args[i] = args[i].astype( np.float32 )                                            # Cast to 32-bit float

  if nargs == 1:
    out = interp1d( data, *args ).astype( inType )
  elif nargs == 2:
    out = interp2d( data, *args ).astype( inType )
  elif nargs == 3:
    out = interp3d( data, *args ).astype( inType )

  if 'missing' in kwargs:                                                               # If missing keyword used
    ids = [slice(None)] * nargs                                                         # Initialize list of slices
    for i in range( nargs ):                                                            # Interate over input indices
      ids[i]          = (args[i] < 0) | (args[i] > (data.shape[i]-1))                   # Locate any out-of-bound indices
      out[tuple(ids)] = kwargs['missing']                                               # Replace values with missing
      ids[i]          = slice(None)                                                     # Replace indices with slice for next loop

  return out                                                                            # Return out
