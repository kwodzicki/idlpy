import numpy as np

def numpy2idl( state ):
  '''
  Function to convert numpy random state tuple to
  IDL format
  '''
  seed      = np.pad( state[1], (2, 2) )
  seed[ 1]  = state[2]
  seed[-2:] = state[3:]
  return seed

def idl2numpy( seed ):
  '''
  Function to convert IDL seed format to numpy ranomd state
  tuple
  '''
  return ('MT19937', seed[2:-2], seed[1], seed[-2], seed[-1])

def randomu( seed, *args, binomial = None, poisson = None):
  '''
  Purpose:
    Function to act similar to IDL RANDOMU
  Inputs:
    seed  :
    *args : list of dimensions
  Keywords:
    binomial :
    poisson  :
  Returns:
    Tuple; (random values,  seed )
  '''
  if len(args) == 1: args = args[0]																						# If single value input, de-tuple

  if isinstance(seed, (tuple, list, np.ndarray)) and len(seed) == 628:			  # If seed is iterable and has len is 628 then
    state = idl2numpy( seed )																								  # Convert seed to numpy state
    np.random.set_state( state )																						  # Set the state
  else:
    np.random.seed( seed )

  if binomial is not None:
    if len(binomial) != 2:
      raise Exception('Must input [n, p] to binomial keyword!')
    x = np.random.binomial( *binomial, args )
  elif isinstance(poisson, (float, int)):
    x = np.random.poisson( poisson, args )
  else:
    x  = np.random.random( args )																							# Compute random values

  seed = numpy2idl( np.random.get_state() )																		# Get current state and convert to IDL convention

  return x, seed 
