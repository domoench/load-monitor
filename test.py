from monitor import loadAvg, loadMedian, highLoad, Monitor
from unittest import main, TestCase

class TestMonitor(TestCase):

  def test_Monitor_1(self):
    m = Monitor()
    self.assertFalse(m.high_load)
    self.assertIsNone(m.min_load)
    self.assertIsNone(m.max_load)

  def test_Monitor_2(self):

    class mock_readSysStats():
      def __init__(self):
        self.stats = []

        # 10 minutes at an average load of 1.5
        for i in range(0, 60):
          now     = i * 10
          load    = float(i) % 4
          up_time = i * 10
          data_point = (now, load, up_time)
          self.stats.append(data_point)

        # 5 more minutes at an average load of 0.5
        for i in range(60, 90):
          now     = i * 10
          load    = float(i) % 2
          up_time = i * 10
          data_point = (now, load, up_time)
          self.stats.append(data_point)

        self.stats_it = iter(self.stats)

      def __call__(self):
        return next(self.stats_it)

    class mock_readData():
      def __init__(self, data):
        self.data = data

      def __call__(self): 
        return self.data

    class mock_saveData():
      def __init__(self, data):
        self.data = data

      def __call__(self, new_data): 
        self.data.clear()
        for k, v in new_data.items():
          self.data[k] = new_data[k]

    test_data = {
      'history': [], 
      'alertHistory': [],
      'uptime'   : None,
      'tenMinAvg': None,
      'minLoad'  : None,
      'maxLoad'  : None,
      'tenMinMed': None,
      'twoMinAvg': None
    }
    m = Monitor()
    m.readSysStats = mock_readSysStats()
    m.readData     = mock_readData(test_data)
    m.saveData     = mock_saveData(test_data)
    m.reschedule   = (lambda: None)
    
    self.assertFalse(m.high_load)

    # Simulate 10 minutes of updates - running at a high load
    for i in range(60):
      m.update_stats()

    self.assertEqual(test_data['tenMinAvg'], 1.5)
    self.assertEqual(test_data['tenMinMed'], 1.5)
    self.assertEqual(test_data['uptime'], 590)
    self.assertEqual(test_data['maxLoad'], 3.0)
    self.assertEqual(test_data['minLoad'], 0.0)
    self.assertEqual(len(test_data['history']), 60)
    
    self.assertEqual(len(test_data['alertHistory']), 1)
    self.assertEqual(test_data['alertHistory'][0][0], 110)
    self.assertTrue(test_data['alertHistory'][0][1])
    self.assertEqual(test_data['alertHistory'][0][2], 1.5)

    self.assertTrue(m.high_load)

    # Simulate 5 more minutes at low load 
    for i in range(60, 90):
      m.update_stats()

    self.assertAlmostEqual(test_data['tenMinAvg'], 1.03333333)
    self.assertEqual(test_data['tenMinMed'], 1.0)
    self.assertEqual(test_data['uptime'], 890)
    self.assertEqual(test_data['maxLoad'], 3.0)
    self.assertEqual(test_data['minLoad'], 0.0)
    self.assertEqual(len(test_data['history']), 60)

    self.assertEqual(len(test_data['alertHistory']), 2)
    self.assertEqual(test_data['alertHistory'][0][0], 660)
    self.assertFalse(test_data['alertHistory'][0][1])
    self.assertEqual(test_data['alertHistory'][0][2], 1.0)
    self.assertEqual(test_data['alertHistory'][1][0], 110)
    self.assertTrue(test_data['alertHistory'][1][1])
    self.assertEqual(test_data['alertHistory'][1][2], 1.5)

    self.assertFalse(m.high_load)

class TestMonitorHelpers(TestCase):

  def test_loadAvg_1(self):
    l = [(60.0, 1.0), (50.0, 1.0), (40.0, 1.0), (30.0, 1.0), (20.0, 1.0), 
         (10.0, 1.0), (0.0, 1.0)]
    self.assertEqual(loadAvg(l), 1.0)

  def test_loadAvg_2(self):
    l = [(60.0, -1.0), (50.0, 1.0), (40.0, -11.0), (30.0, 11.0), 
         (20.0, -991.0), (10.0, 991.0), (0.0, 0.0)]
    self.assertEqual(loadAvg(l), 0.0)

  def test_loadAvg_3(self):
    l = [(60.0, 3.86)]
    self.assertEqual(loadAvg(l), 3.86)

  def test_loadMedian_1(self):
    l = [(60.0, 6.0), (50.0, 2.0), (40.0, 3.0), (30.0, 5.0), (20.0, 4.0), 
         (10.0, 1.0), (0.0, 7.0)]
    self.assertEqual(loadMedian(l), 4.0)

  def test_loadMedian_2(self):
    l = [(60.0, 6.0), (50.0, 2.0), (40.0, 3.0), (30.0, 5.0), (20.0, 4.0), 
         (10.0, 1.0), (0.0, 7.0), (0.0, 8.0)]
    self.assertEqual(loadMedian(l), 4.5)

  def test_loadMedian_3(self):
    l = [(60.0, 1.0), (50.0, 1.0), (40.0, 1.0), (30.0, 1.0), (20.0, 1.0), 
         (10.0, 1.0), (0.0, 1.0)]
    self.assertEqual(loadMedian(l), 1.0)

    l = [(60.0, 6.0)]
    self.assertEqual(loadMedian(l), 6.0)

  def test_highLoad_1(self):
    mins = 10
    l = [(t * 10, 2.0) for t in range(0, 6 * mins)]
    high_load, avg = highLoad(l)
    self.assertTrue(high_load)
    self.assertEqual(avg, 2.0)

    # Reduce load further back than 2 minutes
    for i in range(6 * 2, 6 * mins):
      l[i] = (0.0, 0.0)
    high_load, avg = highLoad(l)
    self.assertTrue(high_load)
    self.assertEqual(avg, 2.0)

  def test_highLoad_2(self):
    mins = 10
    l = [(t * 10, 0.5) for t in range(0, 6 * mins)]
    high_load, avg = highLoad(l)
    self.assertFalse(high_load)
    self.assertEqual(avg, 0.5)

    # Increase load further back than 2 minutes
    for i in range(6 * 2, 6 * mins):
      l[i] = (0.0, 10.0)
    high_load, avg = highLoad(l)
    self.assertFalse(high_load)
    self.assertEqual(avg, 0.5)

  def test_highLoad_3(self):
    l = [(60.0, 5.0), (50.0, 7.0), (40.0, 5.0), (30.0, 10.0)]
    high_load, avg = highLoad(l, 3)
    self.assertFalse(high_load)
    self.assertEqual(avg, 6.75)

main()
