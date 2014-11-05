"""
  This runs constantly in a background process, monitoring the
  system's state (CPU load average history, uptime, statistics) and 
  periodically writing that state to a data store.

  Currently the datastore is a JSON file.
"""

"""
TODO:
  * Handle creating new data.json file when app is just starting up
  * Track min, and max
  * Check load average for past 2 minutes
  * Maintain high_load state
"""

import sched, time, os, json, uptime

s = sched.scheduler(time.time, time.sleep)

high_load = False

def get_uptime():
  t    = time.time()     # Current time
  load = os.getloadavg() # Load for past (1, 5, 15) minutes
  up_t = uptime.uptime() # Total system uptime

  data = {}
  data['uptime'] = up_t
  with open('data.json', 'r+') as f:
    old_data = json.load(f)

    data['history']  = [(t, load[0])] + old_data['history'] 
    data['highload'] = high_load

    if len(data['history']) > 60:
      data['history'].pop()
    assert len(data['history']) <= 60

    f.seek(0)
    json.dump(data, f)
    f.truncate()

  s.enter(10, 1, get_uptime, ())

def loadAvg(l):
  """
  Calculate the average load over a given load history list.

  Args:
    l: A list of (time, cpu-load) tuples
  """
  n = len(l)
  v = 0
  for (t, load) in l:
    v += load
  return v / n


if __name__ == '__main__':
  get_uptime()
  s.run()
