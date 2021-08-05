import csv
import sys
import requests
try:
  import numpy
  HAS_NUMPY = True
except ImportError:
  HAS_NUMPY = False
try:
  import pandas
  HAS_PANDAS = True
except ImportError:
  HAS_PANDAS = False

def _to_csv(x, c):
  return c.join(map(str, x))

def _convert(data):
  if isinstance(data, str):
    d = data
  elif isinstance(data, list):
    d = [_to_csv(ln, ',') if isinstance(ln, list) else ln for ln in data]
    d = _to_csv(d, '\n')
  elif HAS_NUMPY and isinstance(data, numpy.ndarray):
    if (data.ndim == 1):
      d = _to_csv(data, '\n')
    elif (data.ndim == 2):
      d = _to_csv([_to_csv(x, ',') for x in data], '\n')
  elif HAS_PANDAS and isinstance(data, pandas.DataFrame):
      d = _to_csv([_to_csv(x, ',') for x in data.values], '\n')
  elif HAS_PANDAS and isinstance(data, pandas.Series):
      d = _to_csv(data, '\n')
  else:
    d = None
  return d

def _readcsv(fname):
  with open(fname, newline='') as f:
    data = list(csv.reader(f))
  data = [list(map(float,x)) for x in data]
  return data

def _readfile(fname):
  with open(fname) as f:
    data = f.read()
  return data

def _errcode(n):
  if n==2:
    return "Processing"
  elif n==1:
    return "Pending"
  elif n==0:
    return "Ok"
  elif n==-1:
    return "No output"
  elif n==-2:
    return "Not found"
  elif n==-3:
    return "Bad input/params"
  elif n==-4:
    return "Failed"
  elif n==-5:
    return "Server error"
  else:
    return "Unknown error"

def run(data, modelname, pw, e):
  '''
  Starts running a model on the given data
  
  Args:
    data (str or list or numpy.Array or
      pandas.DataFrame or pandas.Series): Dataset over which to run model inference
    modelname (str): name of published model to use
    pw (str): password of model
    e (bool): true if results of the run should be stored longer than one hour
    
  Raises:
    TypeError: Input data must be 1- or 2-dimensional numeric values
  
  Returns:
    dict
      .status_code (int): HTTP status code
      .code (int): Return code
      .msg (str): ForecastID if return code is 0, optional error string on error

  Return code values:
    2: Processing
    1: Pending
    0: OK/Complete
    -1: No value to return
    -2: Job not found
    -3: Bad input params
    -4: Failed
    -5: Server error
  '''
  d = _convert(data)
  if d is None:
    raise TypeError("Invalid input data type")
  
  params = {'d':d, 'm':modelname.lower(), 'p':pw, 'e':e}
  r = requests.post(url="http://api.forecast.university:7706/run", data=params)
  ret = r.json()
  ret['status_code'] = r.status_code
  return ret

def status(id):
  '''
  Checks status of a running inference job
  
  Args:
    id (str): ID string of job
    
  Returns:
    dict
      .status_code (int): HTTP status code
      .code (int): Return code
      .msg (str): Optional, additional messages

  Return code values: see run function docstring
  '''
  params = {'id':id}
  r = requests.post(url="http://api.forecast.university:7706/status", data=params)
  ret = r.json()
  ret['status_code'] = r.status_code
  return ret

def get(id):
  '''
  Retrieves inference results of a job
  
  Args:
    id (str): ID string of job
    
  Returns:
    dict
      .status_code (int): HTTP status code
      .code (int): Return code
      .msg (str): List of str. Note string: not converted to numeric values!

  Return code values: see run function docstring
  '''
  params = {'id':id}
  r = requests.post(url="http://api.forecast.university:7706/get", data=params)
  ret = r.json()
  ret['status_code'] = r.status_code
  return ret
  
def auto(filename, modelname, pw, outfilename):
  data = _readfile(filename)
  
  r = run(data, modelname, pw, True)
  if r['status_code'] != 200:
      print("Server error")
      return
  if (r['code'] != 0):
      print("Run error: " + _errcode(r['code']))
      return
  print("Job queued for execution")
  
  id = r['msg']
  new = True
  while True:
    r = status(id)
    if r['status_code'] != 200:
      print("Server error")
      return
    if r['code'] < 0:
      print("Run failed: " + _errcode(r['code']))
      return
    if new and (r['code'] == 2):
      new = False
      print("Job running")
    if r['code'] == 0:
      print("Job execution complete")
      break
  
  r = get(id)
  if r['status_code'] != 200:
      print("Server error")
      return
  if r['code'] != 0:
      print("Get error: " + _errcode(r['code']))
      return
  
  with open(outfilename, 'w') as f:
    for item in r['msg']:
        f.write("%s\n" % item)
  print("Results written to " + outfilename)
  
if __name__ == "__main__":
  if (len(sys.argv) != 4):
    print("Required args: input-filename, model-name, password")
    print("Eg: python ac.py \"in.csv\" \"user/model\" \"mypwd\"")
  else:
    auto(sys.argv[1], sys.argv[2], sys.argv[3], "forecast.csv")
