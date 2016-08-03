import sys
import math
import time
import random
from collections import defaultdict

def assertEqual(a, b, msg = None):
  if a != b:
    raise Exception('{} does not equal {}! {}'.format(a, b, msg))

class BitArray(object):
  def __init__(self, u):
    self.array = [0 for x in range(u)]

  def insert(self, x):
    self.array[x] = 1

  def delete(self, x):
    self.array[x] = 0

  def successor(self, x):
    index = x + 1
    for val in self.array[x + 1:]:
      if val == 1:
        return index
      else:
        index += 1

  def predecessor(self, x):
    index = x - 1
    for val in self.array[x - 1:0:-1]:
      if val == 1:
        return index
      else:
        index -= 1

class VEB(object):
  def __init__(self, universe_size):
    self.universe_size = int(universe_size)
    self.min = self.max = None
    self.universe_order = math.log2(self.universe_size)
    self.cluster_size = self.high(self.universe_size)
    if self.universe_size > 2:
      self.num_clusters = math.ceil(self.universe_size / self.cluster_size)
      self.clusters = defaultdict(lambda: None)
      self.clusters = [None] * self.num_clusters
      self.summary = VEB(self.num_clusters)
    else:
      self.clusters = None
      self.summary = None

  def __contains__(self, x):
    # the easy cases
    if self.min is None:
      return False
    elif self.min == x:
      return True
    elif x > self.universe_size - 1:
      return False

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
    return x >> math.floor(self.universe_order / 2)

  def low(self, x):
    return x & ( (1 << math.floor(self.universe_order / 2)) - 1)

  def index(self, i, j):
    return i * self.cluster_size + j

  def member(self, x):
    if x == self.min or x == self.max:
      return True
    elif self.universe_size <= 2:
      return False
    else:
      cluster = self.clusters[self.high(x)]
      if cluster != None:
        return cluster.member(self.low(x))
      else:
        return False

  def __str__(self):
    summary = ''
    if self.clusters is None:
      return summary
    for cluster in range(0, len(self.clusters)):
      summary += '['
      for element in range(0, self.cluster_size):
        if self.member(cluster * self.cluster_size + element):
          summary += '1'
        else:
          summary += '0'
      summary += ']'
    return self.summary.__str__() + '\n' + summary

  def insert(self, x):
    if x > (self.universe_size - 1):
      raise Exception('Cannot insert {} into universe sized {}!'.format(x, self.universe_size))
    if self.min is None:
      self.min = self.max = x
      return

    if x == self.min:
      return
    if x < self.min:
      self.min, x = x, self.min
    if x > self.max:
      self.max = x

    if self.universe_size <= 2:
      return

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster is None:
      cluster = self.clusters[cluster_index] = VEB(self.cluster_size)

    if cluster.min is None:
      self.summary.insert(cluster_index)

    cluster.insert(element_index)

  def successor(self, x):
    if self.universe_size <= 2:
      if x == 0 and self.max == 1:
        return 1
      else:
        return None
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
    if self.min is None or x <= self.max:
      return None
    elif x > self.max:
      return self.max

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster and element_index > cluster.min:
      element_index = cluster.predecessor(element_index)
      return self.index(cluster_index, element_index)

    if cluster is None or element_index <= cluster.min:
      cluster_index = self.summary.predecessor(cluster_index)
      element_index = self.clusters[cluster_index].max
      return self.index(cluster_index, element_index)


  def delete(self, x):
    if self.min is None or x < self.min:
      return
    if self.universe_order <= 1:
      if x == self.min:
        self.min = self.max = None
      return

    # If we're trying to delete the minimum value, we've got
    # to figure out what to set the minimum value to, so we
    # need to search through the summary to find it
    # TODO: Refactor this case into separate function
    if x == self.min:
      # in this case, we deleted the last value, so the
      # structure is now completely empty
      if self.summary is None or self.summary.min is None:
        self.min = self.max = None
        return
      cluster_index = self.summary.min
      element_index = self.clusters[cluster_index].min

      # the new minimum is the first item in the next nonzero cluster
      x = self.min = self.index(cluster_index, element_index)

    # This is the more standard case where we don't have to deal
    # with altering the minimum value
    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]
    if cluster is None:
      return
    cluster.delete(element_index)

    if cluster.min is None:
      self.summary.delete(cluster_index)

    # we just deleted the max, so we need to find the predecessor
    if x == self.max:
      # we just deleted the second to last element, so max = min
      if self.summary.max is None:
        self.max = self.min
      else:
        cluster_index = self.summary.max
        element_index = self.clusters[cluster_index].max
        self.max = self.index(cluster_index, element_index)

def test(condition):
  if condition:
    sys.stdout.write('.')
    return True
  else:
    sys.stdout.write('F')
    return False

def time_func(func, n):
  times = []
  for _ in range(0, n):
    start = time.time()
    func()
    times.append(time.time() - start)
  return times

def test_data_structure(instance):
  insert_times = time_func(lambda: instance.insert(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  successor_times = time_func(lambda: instance.successor(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  predecessor_times = time_func(lambda: instance.predecessor(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  delete_times = time_func(lambda: instance.delete(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  print('Average insert time is ' + str(sum(insert_times)/len(insert_times)))
  print('Average successor time is ' + str(sum(successor_times)/len(successor_times)))
  print('Average predecessor time is ' + str(sum(predecessor_times)/len(predecessor_times)))
  print('Average delete time is ' + str(sum(delete_times)/len(delete_times)))

def main():
  #size = pow(2, 16)
  #test_data_structure(BitArray(size))
  #test_data_structure(VEB(size))

  veb = VEB(17)

  values = [ random.randint(0, 16) for _ in range(8) ]
  for val in values:
    veb.insert(val)
  assert(list(veb) == sorted(values))

if __name__ == '__main__':
  main()
