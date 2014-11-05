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
  * Maintain high_load state
"""

import sched, time, os, json, uptime

s = sched.scheduler(time.time, time.sleep)

high_load = False

def get_stats():
  """
  TODO
  """
  t    = time.time()               # Current time
  load = os.getloadavg()           # Load for past (1, 5, 15) minutes
  up_t = int(uptime.uptime() / 60) # Total system uptime in minutes

  data = {}
  data['uptime'] = up_t
  with open('data.json', 'r+') as f:
    old_data = json.load(f)

    data['history']  = [(t, load[0])] + old_data['history'] 

    if len(data['history']) > 60:
      data['history'].pop()
    assert len(data['history']) <= 60

    high_load, two_min_avg = highLoad(data['history'])
    data['highLoad']  = high_load 
    data['twoMinAvg'] = two_min_avg

    # Save to disk
    f.seek(0)
    json.dump(data, f)
    f.truncate()

  # Reschedule
  s.enter(10, 1, get_stats, ())

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

def highLoad(l, mins = 2):
  """
  Determine if the average load over the specified number of recent minutes 
  exceeded 1.0.

  Args:
    l: A list of (time, cpu-load) tuples
    mins: The number of minutes of recent history we're analyzing
  Return:
    Tuple of the form (high load boolean, average load)
  """
  num_samples = mins * 6 
  avg_load  = loadAvg(l[:num_samples])
  high_load = avg_load > 1.0
  return (high_load, avg_load)

if __name__ == '__main__':
  get_stats()
  s.run()
