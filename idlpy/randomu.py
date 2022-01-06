from numpy.random import Generator, MT19937
from numpy import pad, ndarray, float32, float64


class RNG( Generator ):
  def __init__(self):
    super().__init__( MT19937() )
    
  def get_state(self, idl=False):
    """Return state information in numpy or IDL format"""
    state = self.bit_generator.state
    if idl:
      return self._numpy2idl( state )  
    return state

  def set_state(self, state):
    """Update state information, accepts numpy or IDL format"""
    if state is not None:
      if isinstance(state, (tuple, list, ndarray)):
        if len(state) == 628:	# If seed is iterable and has len is 628 then
          state = self._idl2numpy( state )					# Convert seed to numpy state
        else:
          state = MT19937( state[0] ).state                                     #Convert seed to numpy state
      else:
        state = MT19937( state ).state

      self.bit_generator.state = state                                          # Update the state

  def _idl2numpy( self, seed ):
    """Convert IDL seed format to numpy BitGenerator dict format"""
    return {'bit_generator' : 'MT19937',
            'state'         : {'key' : seed[2:-2], 'pos' : seed[1]}}

  def _numpy2idl( self, state ):
    """Convert numpy random state tuple to IDL format"""
  
    seed = pad( state['state']['key'], (2, 2) )
    seed[ 1]  = state['state']['pos']
    return state

# Initialize instance of RNG class 
_RNG = RNG()

def randomu( seed, *args, binomial = None, poisson = None, double=False):
  """
  Create random numbers in similar fasion to IDL RANDOMU()

  Arguments:
    seed  :
    *args : list of dimensions

  Keyword argumentss:
    binomial :
    poisson  :

  Returns:
    Tuple; (random values,  seed )

  """

  _RNG.set_state( seed )
  dtype = float64 if double else float32 

  if len(args) == 0:
    args = 1
  elif len(args) == 1: 
    args = args[0]						# If single value input, de-tuple
    
  if binomial is not None:
    if len(binomial) != 2:
      raise Exception('Must input [n, p] to binomial keyword!')
    x = _RNG.binomial( *binomial, args )
  elif isinstance(poisson, (float, int)):
    x = _RNG.poisson( poisson, args )
  else:
    x  = _RNG.random( args, dtype )																							# Compute random values

  seed = _RNG.get_state(idl=True)																		# Get current state and convert to IDL convention

  return x, seed 
