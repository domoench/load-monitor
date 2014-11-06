"""
  This runs constantly in a background process, monitoring the
  system's state (CPU load average history, uptime, statistics) and 
  periodically writing that state to a data store.

  Currently the datastore is a JSON file.
"""

"""
TODO:
  * Track min, and max
"""

import sched, time, os, json, uptime

class Monitor:

  def __init__(self):
    self.s = sched.scheduler(time.time, time.sleep)
    self.high_load = False       # True => Average load over past 2 mins > 1.0
    self.min_load  = None
    self.max_load  = None

    with open('data.json', 'w') as f:
      data = {'history': [], 'alertHistory': []}
      json.dump(data, f)

  def update_stats(self):
    """
    TODO
    """
    # Get system stats
    now  = time.time()               # Current time
    load = os.getloadavg()           # Load for past (1, 5, 15) minutes
    up_t = int(uptime.uptime() / 60) # Total system uptime in minutes

    with open('data.json', 'r+') as f:
      old_data = json.load(f)

      # Add newest data point to history
      history = old_data['history'] 
      history.insert(0, (now, load[0]))
      if len(history) > 60:
        history.pop()
      assert len(history) <= 60

      # Update min, max, and 10-min mean and median
      if not self.min_load:
        self.min_load = load[0]
        self.max_load = load[0]
      else:
        if load[0] < self.min_load:
          self.min_load = load[0]
        if load[0] > self.max_load:
          self.max_load = load[0]

      # Check if load state crossed alert threshold
      alert_history = old_data['alertHistory']
      new_high_load, two_min_avg = highLoad(history)
      if new_high_load != self.high_load:
        alert_history.insert(0, (now, new_high_load, two_min_avg))
        self.high_load = new_high_load
        # TODO: Prune alert_history if it goes to far back into past

      # Package up and save to disk
      data = {}
      data['twoMinAvg'] = two_min_avg
      data['tenMinAvg'] = loadAvg(history)
      data['tenMinMed'] = loadMedian(history)
      data['history']   = history
      data['uptime']    = up_t
      data['minLoad']   = self.min_load
      data['maxLoad']   = self.max_load
      data['alertHistory'] = alert_history

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
    l: A list of (time, cpu-load) tuples - the history.
  """
  n = len(l)
  v = 0
  for (t, load) in l:
    v += load
  return v / n

def loadMedian(l):
  """
  Calculate the median load over a given load history list.

  Args:
    l: A list of (time, cpu-load) tuples - the history.
  """
  n = len(l)
  loads = [load for time, load in l]
  sorted_loads = sorted(loads)
  if not n % 2:
    return (sorted_loads[n / 2] + sorted_loads[n / 2 - 1]) / 2.0
  return sorted_loads[n / 2]

def highLoad(l, mins = 2):
  """
  Determine if the average load over the specified number of recent minutes 
  exceeded 1.0. If the history list does cover the requested number of 
  minutes, the high load will return false.

  Args:
    l: A list of (time, cpu-load) tuples - the history.
    mins: The number of minutes of recent history we're analyzing.
  Return:
    Tuple of the form (high load boolean, average load)
  """
  num_samples = mins * 6 
  avg_load  = loadAvg(l[:num_samples])
  high_load = len(l) >= num_samples and avg_load > 1.0
  return (high_load, avg_load)

if __name__ == '__main__':
  m = Monitor()
  m.run()
