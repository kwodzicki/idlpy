import logging
import os, re

###############################################################################
def file_search( indir, pattern = None, match_all_initial_dot = False):
  """
  Name:
      file_search
  Purpose:
      Function that acts like the IDL FILE_SEARCH() function
  Inputs:
  """
  out   = []
  if (pattern is None):
    for f in os.listdir(indir):
      fpath = os.path.join(indir, f)
      if os.path.isfile(fpath):
        out.append(fpath)
  else:
    pattern = '^{}$'.format( pattern.replace('*', '.*') );                  # Conver pattern to regular expression where * is replaced by .*
    for root, dirs, files in os.walk(indir):
      for f in files:
        if (not match_all_initial_dot) and (f[0] == '.'): continue;     # If match_all_initial_dot is False, and the file name starts with '.', skip it
        fpath = os.path.join( root, f );
        if os.path.isfile( fpath ):
          matches = re.findall(pattern, f)
          if len(matches) >= 1:
            out.append( fpath )
  return out, len(out)
