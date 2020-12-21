from datetime import datetime

class JTime( object ):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.jday    = 0
    self.seconds = 0
    self.no_leap = kwargs.get('no_leap', False)

  def __sub__(self, val):
    if isinstance(val, JTime):
      return 86400 * (self.jday - val.jday) + (self.seconds-val.second)
#    elif isinstance(val, datetime):
#      return self - make_time(val.year, val.month, val.day,
#                              val.hour, val.minute, val.second)
