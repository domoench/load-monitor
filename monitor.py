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
"""

import sched, time, os, json, uptime

class Monitor:

  def __init__(self):
    self.s = sched.scheduler(time.time, time.sleep)
    self.load_state_t = time.time() # Time when current load state began
    self.high_load    = False       # True => Average load over past 2 mins > 1.0

  def update_stats(self):
    """
    TODO
    """
    # Get system stats
    t    = time.time()               # Current time
    load = os.getloadavg()           # Load for past (1, 5, 15) minutes
    up_t = int(uptime.uptime() / 60) # Total system uptime in minutes

    with open('data.json', 'r+') as f:
      old_data = json.load(f)

      # Add newest data point to history
      history = [(t, load[0])] + old_data['history'] 
      if len(history) > 60:
        history.pop()
      assert len(history) <= 60

      # Check if load state crossed alert threshold
      hl, two_min_avg = highLoad(history)
      if hl != self.high_load:
        self.high_load = hl
        load_state_t   = t

      # Package up and save to disk
      data = {}
      data['history']   = history
      data['highLoad']  = self.high_load 
      data['stateTime'] = self.load_state_t
      data['twoMinAvg'] = two_min_avg
      data['uptime']    = up_t

      f.seek(0)
      json.dump(data, f)
      f.truncate()

    # Reschedule
    self.s.enter(10, 1, self.update_stats, ())

  def run(self):
    self.update_stats()
    self.s.run()

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
  # TODO: What if num_samples > len(l)? Like when you first fire up the app?
  avg_load  = loadAvg(l[:num_samples])
  high_load = avg_load > 1.0
  return (high_load, avg_load)

if __name__ == '__main__':
  m = Monitor()
  m.run()
