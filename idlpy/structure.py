class Structure(object):
  """
  Class to act similar to an IDL structure and python dictionary.

  Note:
    All attributes/keys are forced to lower case

  """

  def __init__(self, **kwargs):
    """
    Initialize the class

    Arguments:
      None

    Keyword arguments:
      Tag/value pairs to create structure

    Returns:
      Structure instance

    """
    for key, val in kwargs.items():                                                     # Iterate over all key/value pairs in kwargs
      self[key] = val                                                                   # Define new value

  def __getitem__(self, key, default = None):
    """Method for getting data using obj[key] syntax"""
    return self.__dict__.get(key.lower(), default)                                      # Get data, force key to lower case 

  def __setitem__(self, key, val):
    """Method for setting data using obj[key] syntax"""
    self.__dict__[key.lower()] = val                                                    # Set value, force key to lower case

  def __getattr__(self, key):
    """Method for getting data using obj.key syntax"""
    return self[key]

  def __setattr__(self, key, val):
    """Method for setting data using obj.key syntax"""
    self[key] = val

  def __contains__(self, key):
    """Method for checking if key in structure"""
    return key.lower() in self.__dict__

  def keys(self):
    """Method for getting all keys in structure"""
    return self.__dict__.keys()
