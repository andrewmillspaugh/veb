import sys
import math
import time
import random
from collections import defaultdict

LEAF_WORD_SIZE = 2

class VEBLeaf(object):
  def __init__(self, word_size):
    self.word_size = word_size
    self.values = [False] * pow(2, self.word_size)

  def __iter__(self):
    return (index for index, value in enumerate(self.values) if value)

  def __reversed__(self):
    return (len(self.values) - index - 1 for index, value in enumerate(reversed(self.values)) if value)

  @property
  def min(self):
    return next(iter(self), None)

  @property
  def max(self):
    return next(reversed(self), None)

  def insert(self, x):
    self.values[x] = True

  def delete(self, x):
    self.values[x] = False

  def successor(self, x):
    if (x + 1) >= len(self.values):
      return None
    else:
      try:
        return self.values[x + 1:].index(True) + x + 1
      except ValueError:
        return None

  def predecessor(self, x):
    if x <= 0:
      return None
    else:
      try:
        return x - self.values[x - 1::-1].index(True) - 1
      except ValueError:
        return None

class VEBTree(object):
  def __init__(self, word_size):
    self.min = self.max = None
    self.word_size = word_size
    self.summary_size = int(math.ceil(self.word_size / 2))
    self.clusters = [None] * (1 << self.summary_size)
    self.summary = VEB.of_size(self.summary_size)

  def __contains__(self, x):
    if self.min is None:
      return False
    elif self.min == x:
      return True
    else:
      high = self.high(x)
      low = self.low(x)
      if self.clusters[high] is None:
        return False
      else:
        return low in self.clusters[high]

  def __iter__(self):
    # empty tree
    if self.min is None:
      return

    # special case for min value
    yield self.min

    current = self.min
    while current != self.max:
      current = self.successor(current)
      yield current

  def high(self, x):
    return x >> int(self.summary_size)

  def low(self, x):
    return x & ( (1 << int(self.summary_size)) - 1)

  def index(self, i, j):
    return i * pow(2, self.summary_size) + j

  def insert(self, x):
    if self.min is None:
      self.min = self.max = x
      return

    if x == self.min:
      return
    if x < self.min:
      self.min, x = x, self.min
    if x > self.max:
      self.max = x

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster is None:
      cluster = self.clusters[cluster_index] = VEB.of_size(self.summary_size)

    if cluster.min is None:
      self.summary.insert(cluster_index)

    cluster.insert(element_index)

  def successor(self, x):
    if self.min is None or x >= self.max:
      return None
    elif x < self.min:
      return self.min

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster and element_index < cluster.max:
      element_index = cluster.successor(element_index)
      return self.index(cluster_index, element_index)
    else:
      cluster_index = self.summary.successor(cluster_index)
      element_index = self.clusters[cluster_index].min
      return self.index(cluster_index, element_index)

  # perfectly symmetric with successor
  def predecessor(self, x):
    if self.min is None or x <= self.min:
      return None
    elif x > self.max:
      return self.max

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster is None or element_index <= cluster.min:
      cluster_index = self.summary.predecessor(cluster_index)
      element_index = self.clusters[cluster_index].max
      return self.index(cluster_index, element_index)
    else:
      element_index = cluster.predecessor(element_index)
      return self.index(cluster_index, element_index)


  def delete(self, x):
    if self.min is None or x < self.min:
      return

    if x == self.min:
      if self.summary is None or self.summary.min is None:
        self.min = self.max = None
        return
      cluster_index = self.summary.min
      element_index = self.clusters[cluster_index].min

      x = self.min = self.index(cluster_index, element_index)

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]
    if cluster is None:
      return
    cluster.delete(element_index)

    if cluster.min is None:
      self.summary.delete(cluster_index)

    if x == self.max:
      if self.summary.max is None:
        self.max = self.min
      else:
        cluster_index = self.summary.max
        element_index = self.clusters[cluster_index].max
        self.max = self.index(cluster_index, element_index)

class VEB(object):
  def __init__(self):
    raise NotImplemented()

  @classmethod
  def of_size(cls, word_size):
    return VEBLeaf(word_size) if word_size <= LEAF_WORD_SIZE else VEBTree(word_size)

def main():
  word_size = 16
  veb = VEB.of_size(word_size)

  values = [ random.randint(0, pow(2, word_size) - 1) for _ in range(pow(2, word_size - 1)) ]
  for val in values:
    veb.insert(val)
  print('Does veb work?: {}'.format(list(veb) == sorted(set(values))))

if __name__ == '__main__':
  main()
