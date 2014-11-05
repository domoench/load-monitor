"""
  This runs constantly in a background process, monitoring the
  system's state (CPU load average history, uptime, statistics) and 
  periodically writing that state to a data store.

  Currently the datastore is a JSON file.
"""

import sched, time, os

s = sched.scheduler(time.time, time.sleep)

def get_uptime():
  print(str(time.time()) + ': ' + str(os.getloadavg()))
  s.enter(10, 1, get_uptime, ())
  s.run()

get_uptime()
