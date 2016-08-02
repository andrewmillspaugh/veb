import random
import unittest

from veb import VEB

class TestVEB(unittest.TestCase):
    def setUp(self):
      self.size = pow(2, 4)
      self.veb = VEB(self.size)
    
    def test_insert(self):
      vals = set(random.randint(1, self.size - 1) for _ in range(self.size//2))
      for x in vals:
        self.veb.insert(x)
      for x in range(0, self.size):
        if x in vals:
          self.assertIn(x, self.veb)
        else:
          self.assertNotIn(x, self.veb)
      self.assertEqual(self.veb.min, min(vals))
      self.assertEqual(self.veb.max, max(vals))
