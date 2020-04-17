import logging
import os, re, time
from datetime import datetime, timedelta
from threading import Thread
from subprocess import Popen, PIPE

###############################################################################
class IDLJob( object ):
  _finishedMSG = 'spawnIDL FINISHED!!!';                                                # Custom message to signal that IDL process completed successfully
  def __init__(self, cmd, _UTC=False, _STDOUTLVL=logging.INFO, _STDERRLVL=logging.DEBUG, **kwargs):
    self.log        = logging.getLogger(__name__);                                         # Get a logger
    self.IDLcmd     = None;                                                                # Initialize IDLcmd to None
    self.fullcmd    = None;                                                                # Initialize fullcmd to None
    self.failed     = None;                                                                # Initialize failed to None
    self.isfunc     = False;                                                               # Initialize isfunc to False
    self._UTC       = _UTC;                                                                # Set whether dates are UTC time
    self._STDOUTLVL = _STDOUTLVL
    self._STDERRLVL = _STDERRLVL
    self._proc      = None;
    self._stdout    = None;
    self._stderr    = None;
    self._parseArgs( cmd, **kwargs );                                                   # Parse input arguments

  #############################################################################
  def start(self, nowait = False):
    """
    Name:
      start
    Purpose:
      Method that starts the IDL subprocess and the threads that pipe
      stdout and stderr to a logger
    Inputs:
      None
    Ouputs:
      Returns True if IDL process was success, False otherwise
    Keywords:
      nowait : If set to True, will not wait for subprocess to finish. On
                return gives value of failed; i.e., True if process failed,
                False if ran. If set to True, returns None right away.
                DEFAULT is to block until process finished and return the
                value of failed attribute
    """
    self.failed = True;                                                                 # Set failed to True, will be set to false by threads if completes
    my_env = os.environ.copy();                                                         # Copy user's environment
    if ('IDL_STARTUP' not in my_env):                                                   # If noe IDL_STARTUP set in environment
        startup = os.path.join( os.path.expanduser('~'), 'startup.pro' );               # Assume startup.pro in home directory
        if os.path.isfile( startup ):                                                   # If the assumed file exists
            my_env['IDL_STARTUP'] = startup;                                            # Use it for start up

    if ('IDL_STARTUP' in my_env):
        self.log.debug( 'Using startup file : {}'.format(my_env['IDL_STARTUP']))

    self._proc  = Popen( self.fullcmd, stdout = PIPE, stderr = PIPE, 
                      cwd                = os.path.expanduser('~'),
                      env                = my_env,
                      universal_newlines = True );                                      # Start the IDL process
    self._stdout = Thread( target=self._logSTD, args=(self._STDOUTLVL, self._proc.stdout,) );   # Initialize thread to log stdout to logger
    self._stderr = Thread( target=self._logSTD, args=(self._STDERRLVL, self._proc.stderr,) );   # Initialize thread to log stderr to logger

    self._stdout.start();                                                               # Start thread to pipe stdout
    self._stderr.start();                                                               # Start thread to pipe stderr

    if nowait:                                                                          # If the nowait keyword is set
        return None;                                                                    # Return None
    else:                                                                               # Else
        return self.wait();                                                             # Return result of the wait() method; returns failed state

  #############################################################################
  def wait(self):
    self._stdout.join()
    self._stderr.join()
    self._proc.communicate()

    return self.failed

  #############################################################################
  def is_alive(self):
    """
    Name
      is_alive
    Purpose:
      check if subprocess is still running
    Inputs:
      None.
    Outputs:
      True if running, false if done
    """
    return (self._proc.poll() is None);                                         # If poll() method returns None, then still running

  #############################################################################
  def _parseArgs(self, cmd, **kwargs):
    """"
    Name:
      _parseArgs
    Purpose:
      A method to parse IDL cmd string into arguments, setting arguments
      using values from keywords.
    Inputs:
      cmd   : IDL command to run as string with all arugments
    Outputs:
      None
    Keywords:
      All variables required by IDL command.
      THESE ARE CASE-SENSITIVE AND MUST MATCH cmd EXACTLY!!!!
    """
    if isinstance( cmd, (list,tuple,) ): cmd = ', '.join(cmd);                          # If the command input is a list or tuple, join on comma into one long string
    args = re.findall( r'\((.*)\)', cmd );                                              # Try to get arguments from IDL function command; i.e, all text between ( )
    if len(args) == 1:                                                                  # If text was found between parenthases
      self.isfunc = True;                                                               # Set isfunc attribute to True
      args        = args[0].split(',');                                                 # Split the arguments on comma
    else:                                                                               # Else, is a procedure
      args = cmd.split(',')[1:];                                                        # Split on comma, taking second through last value; first value is procedure name

    self.IDLcmd = [];                                                                   # Initialize list to store IDL cmds
    for arg in args:                                                                    # Iterate over the arguements
      varName = arg.split('=')[-1].strip();                                             # Get variable name from argument; if keyword, then variable name is AFTER equals sign
      varVal  = kwargs.get(varName, None);                                              # Get variable value from keywords, None if no variable in keywords
      if (varVal is not None):                                                          # If variable value is NOT None
        if isinstance(varVal, datetime):                                                # If datetime object passed in
          varVal = make_iso_date_string( varVal, utc = self._UTC );                     # Convert datetime to string in ISO 9601 format
          self.IDLcmd += ["{} = READ_ISO_DATE_STRING('{}')".format(varName, varVal)];   # Command will parse date string into {CDATE} IDL structure
        elif (type(varVal) is bool):                                                    # If it is a boolean
          varVal       = 1 if (varVal is True) else 0;                                  # Set varVal to one (1) if True, zero (0) if False
          self.IDLcmd += ["{} = {}".format(varName, varVal)];                           # Just set value
        elif (type(varVal) is str):                                                     # If value is string type
          if os.path.isdir(varVal):                                                     # If string is a valid directory
            varVal = os.path.join(varVal, '');                                          # Ensure has trailing separator on it
          self.IDLcmd += ["{} = '{}'".format(varName, varVal)];                         # Add command to list, setting variable as quoted string
        else:                                                                           # Else
          self.IDLcmd += ["{} = {}".format(varName, varVal)];                           # Just set value

    self.IDLcmd += [cmd];                                                               # Append full command to list
    self.IDLcmd += ["MESSAGE, '{}', /CONTINUE".format( self._finishedMSG )];            # Append IDL message call with custom text to signal that process completed
    self.IDLcmd  = ' & '.join( self.IDLcmd );                                           # Join IDLcmd list on ' & ' and place in double quotes
    self.fullcmd = ['idl', '-e', self.IDLcmd];                                          # Command to spawn
#    self.fullcmd = ['idl', '-arg', 'bowman', '-e', self.IDLcmd];                                          # Command to spawn
    self.log.debug( 'IDL command: {}'.format( ' '.join(self.fullcmd) ) )
 
  #############################################################################
  def _logSTD( self, level, pipe ):
    """
    Name:
      _logSTD
    Purpose:
      A method to read text from a pipe and send it to a logger
      at a given log level
    Inputs:
      level  : The level to log at
      pipe   : Pipe to read from
    Outputs:
      None.
    Keywords:
      None.
    """
    line = pipe.readline();                                                     # Read a line from the pipe
    while line != '':                                                           # While the line is not empty
      self.log.log( level, line.rstrip() );                                     # As the line to the logger; strip off all return characters
      if (self._finishedMSG in line):                                           # If the _finishedMSG is in the line
        self.failed = False;                                                    # Set failed to False
      line = pipe.readline();                                                   # Read another line from the pipe

##############################################################################
class IDLAsyncQueue( object ):
  def __init__(self, concurrency = CONFIG['NCPU']):
    self.concurrency = concurrency
    self._queue     = [];
    self._njobs     = 0
    self._jobs      = [];
    self._jobpass   = [];
    self._thread    = None;

  #############################################################################
  def submitJob(self, job):
    """
    Name:
      submitJob
    Purpose:
      Method to submit a spawnIDL object to the queue
    Inputs:
      job   : A spawnIDL object
    Outputs:
      None.
    """
    if isinstance( job, IDLJob ):
      self._njobs += 1;
      self._queue.append( job );

  #############################################################################
  def startJobs(self, nowait = False):
    """
    Name:
      startJobs
    Purpose:
      A method to start running jobs in the queue
    Inputs:
      None.
    Outputs:
      Typically returns a tuple where first element is number of jobs
      that completed successfully and seoncd element is total number of
      jobs run. However, if the nowait keyword is set, will return None.
    Keywords:
      nowait  : If set, method will start thread to manage jobs and return
                 immediately. Should only be used in special cause, but
                 is intended to allow user to keep submitting jobs
                 to queue. 
                 NOTE: It is possible that the job queue could 
                 empty before one submits a new job, which means the new
                 job wont start until this method is called again
    """
    self._thread = Thread(target = self._run);                                  # Initialize thread to run the _run method
    self._thread.start();                                                       # Start the thread
    if nowait:                                                                  # If nowait is set
      return None, None;                                                        # Return None tuple
    else:                                                                       # Else
      return self.join();                                                       # Call join method

  #############################################################################
  def join(self):
    """
    Name:
      join
    Purpose:
      A method to wait for all jobs in the queue to finish
    Inputs:
      None.
    Outputs:
      Returns tuple where first element is number of jobs that ran
      successfully and second element is total number of jobs run.
      In a perfect world, these two numbers would always equal eachother.
      NOTE: If the startJobs method was never called, then this method will
            return (None, None,)
    Keywords:
      None.
    """
    if (self._thread is not None):                                              # If the _thread attribute is not None
      self._thread.join();                                                      # Join the thread, i.e., wait for it to finish
      nsuccess, ntot = sum( self._jobpass ), self._njobs;                       # Number of successful (i.e., NOT failed) and # total jobs
      self.__reset();                                                           # Reset all values
      return nsuccess, ntot;                                                    # Return # successful and # total jobs
    return None, None
  #############################################################################
  def _run(self):
    """
    Name:
      _run
    Purpose:
      method to actually run/manage all the process in the queue
    Inputs:
      None.
    Outputs:
      None.
    """
    while len(self._queue) > 0:                                                     # While there are jobs in the queue
      self._manage();                                                               # Block until process finishes if too many running 
      job = self._queue.pop(0);                                                     # Pop job object off of queue
      job.start( nowait = True );                                                   # Start and do NOT wait to finish (non-blocking)
      self._jobs.append( job );                                                     # Append job to jobs arrray 
    self._manage( waitall = True );                                                 # Wait for rest of jobs to finish

  #############################################################################
  def _manage(self, waitall = False, update = 0.1):
    """
    Name:
      _manage
    Purpose:
      A method intended to block until a process opens up. This means
      if concurrency is set to 4 and 4 processes are running, we continually
      check until a process finishes. When one finishes, the method returns
    Inputs:
      None.
    Outputs:
      None.
    Keywords:
      waitall  : If set, block until all running jobs finish
      update   : Sleep interval (in seconds) between checks for jobs
                  finished
   """
    njobs = 1 if waitall else self.concurrency;                                     # Set njobs to one (1) if waitall is set, else use concurrency
    while len(self._jobs) > (njobs-1):                                              # While number of jobs is greater than one less the allowed number of jobs
      for i in range( len(self._jobs) ):                                            # Iterate over all job objects
        if not self._jobs[i].is_alive():                                            # If the job is NOT alive
          job = self._jobs.pop(i);                                                  # Pop off the job
          self._jobpass.append( not job.wait() );                                   # Get the opposite of failure state of job and append _jobpass list
          break;                                                                    # Break the for loop
      time.sleep( update );                                                         # Sleep for 100 miliseconds

  #############################################################################
  def __reset(self):
    """ Method to 're-initialize' the class"""
    self._queue   = [];
    self._njobs   = 0
    self._jobs    = [];
    self._jobpass = [];
    self._thread  = None;


