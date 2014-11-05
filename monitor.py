"""
  This runs constantly in a background process, monitoring the
  system's state (CPU load average history, uptime, statistics) and 
  periodically writing that state to a data store.

  Currently the datastore is a JSON file.
"""

import sched, time, os, json, uptime

s = sched.scheduler(time.time, time.sleep)

def get_uptime():
  t    = time.time()     # Current time
  load = os.getloadavg() # Load for past (1, 5, 15) minutes
  up_t = uptime.uptime() # Total system uptime

  data = {}
  data['uptime'] = up_t
  with open('data.json', 'r+') as f:
    old_data = json.load(f)

    data['history'] = [(t, load[0])] + old_data['history'] 

    if len(data['history']) > 60:
      data['history'].pop()
    assert len(data['history']) <= 60

    f.seek(0)
    json.dump(data, f)
    f.truncate()

  s.enter(10, 1, get_uptime, ())

get_uptime()
s.run()
