"""
  This runs constantly in a background process, monitoring the
  system's state (CPU load average history, uptime, statistics) and 
  periodically writing that state to a data store.

  Currently the datastore is a JSON file.
"""

import sched, time, os, json

s = sched.scheduler(time.time, time.sleep)

def get_uptime():
  t    = time.time()
  load = os.getloadavg()
  print(str(t) + ': ' + str(load))

  data = {}
  data['time'] = t
  data['load'] = load[0] # One minute load-avg

  with open('data.json', 'w') as f:
    json.dump(data, f)

  s.enter(10, 1, get_uptime, ())
  s.run()

get_uptime()
