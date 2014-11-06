from monitor import loadAvg, highLoad
from unittest import main, TestCase

class TestMonitor(TestCase):

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
