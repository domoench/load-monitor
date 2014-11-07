"""
  This process monitors the system's state (CPU load average history, uptime, 
  statistics) and writes that state to a JSON data store every 10 seconds.
"""
import sched, time, os, json, uptime, multiprocessing

class Monitor:

  def __init__(self):
    self.s = sched.scheduler(time.time, time.sleep)
    self.high_load = False  # True => Average load over past 2 mins > 1.0
    self.min_load  = None
    self.max_load  = None
    self.num_cores = multiprocessing.cpu_count()

    # Write datastore template
    with open('data.json', 'w') as f:
      data = {'history': [], 'alertHistory': []}
      json.dump(data, f)

  def update_stats(self):
    """
    Repeatedly read system state (load and uptime), calculate some statistics,
    check if we're in a 'high load' state, and save all data to JSON datastore.

    A 'high load' state means the average load over the past 2 minutes exceeds
    1.0.

    Load history is a list of load samples taken every 10 seconds, extending 
    back 10 minutes:
      history = [(t0, load0), (t1, load0), (t2, load2), ...]
    Where t0 is 0 seconds ago, t1 is 10 seconds ago, t2 is 20 seconds ago, etc.

    Alert history is a list of events marking in and out of high load state:
      alert_history = [(t0, ls0, avg0), (t3, ls3, avg3), ...]
    Where the first tuple is the most recent state change. t0 is the time of the
    event, ls0 is the new high load state (Boolean), and avg0 is the 2-minute
    load average at that time.
    """
    # Get system stats
    now   = time.time()               # Current time
    loads = os.getloadavg()           # Load for past (1, 5, 15) minutes
    up_t  = int(uptime.uptime() / 60) # Total system uptime in minutes

    # Normalize load according to number of CPU cores
    load = loads[0] / self.num_cores 

    with open('data.json', 'r+') as f:
      old_data = json.load(f)

      # Add newest data sample to history.
      history = old_data['history'] 
      history.insert(0, (now, load))
      if len(history) > 60:
        history.pop()
      assert len(history) <= 60

      # Update min, max 
      if not self.min_load:
        self.min_load = load
        self.max_load = load
      else:
        if load < self.min_load:
          self.min_load = load
        if load > self.max_load:
          self.max_load = load

      # Check if load state crossed alert threshold
      alert_history = old_data['alertHistory']
      new_high_load, two_min_avg = highLoad(history)
      if new_high_load is not self.high_load:
        alert_history.insert(0, (now, new_high_load, two_min_avg))
        self.high_load = new_high_load
        # TODO: Prune alert_history if it goes to far back into past?

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
    l: A list of (time, cpu-load) tuples.
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
    l: A list of (time, cpu-load) tuples.
  """
  n = len(l)
  loads = sorted((load for time, load in l))
  if not n % 2:
    return (loads[n / 2] + loads[n / 2 - 1]) / 2.0
  return loads[n / 2]

def highLoad(l, mins = 2):
  """
  Determine if the average load over the recent past exceeded 1.0. The recent
  past is the most recent 'mins' minutes. If the history list does cover the 
  requested number of minutes, the high load will return false.

  Args:
    l: A list of (time, cpu-load) tuples.
    mins: The number of minutes of recent history we're analyzing.
  Return:
    Tuple of the form (high load boolean, average load)
  """
  sample_len = mins * 6 
  avg_load   = loadAvg(l[:sample_len])
  high_load  = len(l) >= sample_len and avg_load > 1.0
  return (high_load, avg_load)

if __name__ == '__main__':
  m = Monitor()
  m.run()
