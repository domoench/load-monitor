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
    self.data_path = 'data.json'

    # Write datastore template
    with open(self.data_path, 'w') as f:
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
    now, load, up_time = self.readSysStats()
    old_data = self.readData()

    # Add newest data sample to history.
    history = old_data['history'] 
    history.insert(0, (now, load))
    if len(history) > 60:
      history.pop()
    assert len(history) <= 60

    # Update min, max 
    if self.min_load is None:
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

    # Package up and save to disk
    new_data = {}
    new_data['twoMinAvg'] = two_min_avg
    new_data['tenMinAvg'] = loadAvg(history)
    new_data['tenMinMed'] = loadMedian(history)
    new_data['history']   = history
    new_data['uptime']    = up_time
    new_data['minLoad']   = self.min_load
    new_data['maxLoad']   = self.max_load
    new_data['alertHistory'] = alert_history
    
    self.saveData(new_data)

    # Reschedule
    self.reschedule()

  def readSysStats(self):
    now  = time.time()               
    load = self.getLoad()            
    up_time = int(uptime.uptime() / 60.0) 
    return (now, load, up_time)

  def readData(self):
    with open(self.data_path, 'r') as f:
      return json.load(f)

  def saveData(self, data):
    with open(self.data_path, 'w') as f:
      json.dump(data, f)

  def getLoad(self):
    """
    Get the CPU load normalized by the number of cores.
    """
    loads = os.getloadavg()   # Load for past (1, 5, 15) minutes
    return loads[0] / self.num_cores 

  def reschedule(self):
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
