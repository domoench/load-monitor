from monitor import loadAvg
from unittest import main, TestCase

class TestMonitor(TestCase):

  def test_loadAvg_1(self):
    l = [(60.0, 1.0), (50.0, 1.0), (40.0, 1.0), (30.0, 1.0), (20.0, 1.0), 
         (10.0, 1.0), (0.0, 1.0)]
    self.assertEqual(loadAvg(l), 1.0)

  def test_loadAvg_2(self):
    l = [(60.0, -1.0), (50.0, 1.0), (40.0, -11.0), (30.0, 11.0), (20.0, -991.0), 
         (10.0, 991.0), (0.0, 0.0)]
    self.assertEqual(loadAvg(l), 0.0)

  def test_loadAvg_3(self):
    l = [(60.0, 3.86)]
    self.assertEqual(loadAvg(l), 3.86)

main()
