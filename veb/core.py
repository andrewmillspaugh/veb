import sys
import math
import time
import random
from collections import defaultdict

# O(1) insert/delete
# O(n) next/prev
class BitArray(object):
  def __init__(self, u):
    self.array = [0 for x in range(u)]

  def insert(self, x):
    self.array[x] = 1

  def delete(self, x):
    self.array[x] = 0

  def next(self, x):
    index = x + 1
    for val in self.array[x + 1:]:
      if val == 1:
        return index
      else:
        index += 1

  def prev(self, x):
    index = x - 1
    for val in self.array[x - 1:0:-1]:
      if val == 1:
        return index
      else:
        index -= 1

class VEB(object):
  def __init__(self, universe_size):
    # x = i*sqrt(u) + j
    self.universe_size = universe_size
    self.min = self.max = None
    self._universe_order = 1 << math.ceil(math.log2(self.universe_size) / 2)
    if self._universe_order > 1:
      self.clusters = defaultdict(lambda: None)
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

  # the high order bits from a cluster
  # equivalent to i in x = i*sqrt(universe_size) + j
  def high(self, x):
    return x // self._universe_order

  # the low order bits from a cluster
  # equivalent to j in x = i*sqrt(universe_size) + j
  def low(self, x):
    return x % self._universe_order

  def index(self, i, j):
    return int(i*math.sqrt(self.universe_size) + j)

  # we need to insert both into the appropriate cluster as well
  # as insert into the summary structure, because we just inserted
  # something into a cluster, so we better make sure that the
  # summary structure reflects that
  def insert(self, x):
    # if nothing is stored in min, lazily store x in the min (as well as the max).
    # this is the only case in which x doesn't have to be recursively inserted
    if self.min is None or self._universe_order == 1:
      self.min = self.max = x
      return

    # something is already in min, so we have to figure out where to put it and,
    # because we know that the cluster isnt empty, we also have to deal with max

    # the new x is smaller than the existing min, so we need to swap them
    if x < self.min:
      self.min, x = x, self.min
    # the new x is bigger than the existing min, so we can blindly set it
    if x > self.max:
      self.max = x

    cluster_index = self.high(x)
    element_index = self.low(x)

    # we build the summary structure lazily
    if self.summary is None:
      self.summary = VEB(self.high(self.universe_size))

    # we build the clusters lazily
    if self.clusters[cluster_index] is None:
      self.clusters[cluster_index] = VEB(self.high(self.universe_size))

    # if if the cluster doesn't have a min, we know we need to also update
    # the summary structure to reflect our insert
    if self.clusters[cluster_index].min is None:
      self.summary.insert(cluster_index)

    # if we went through the above branch where self.clusters[cluster_index].min is None,
    # then we know that this cluster also has min is None, which means that this will
    # be a constant time operation. Therefore, we always only have one recursive call
    self.clusters[cluster_index].insert(element_index)

  # first, we look in x's cluster (clusters[high(x)]) and then
  # we look in the summary structure for the next 1 bit, and look
  # in that cluster for the first 1 bit (which will be the successor)
  def next(self, x):
    # this tree is empty, or x is the biggest in it
    if self.min is None or x >= self.max:
      return None
    elif x <= self.min:
      return self.min

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    # we know the sucessor is in this cluster because we have a
    # valid cluster and the value we're looking for is smaller
    # than the max. So, simply return the sucessor in this cluster.
    if cluster and element_index < cluster.max:
      element_index = cluster.next(element_index)
      return self.index(cluster_index, element_index)

    # we know the successor isn't here, because either the cluster
    # is empty, or we asked for the successor of something bigger
    # than the max in the cluster. So, we'll instead look for the
    # next 1 bit in the summary structure, and then look through
    # that cluster for our successor
    if cluster is None or element_index >= cluster.max:
      cluster_index = self.summary.next(cluster_index)
      element_index = self.clusters[cluster_index].min
      return self.index(cluster_index, element_index)

  # perfectly symmetric with next
  def prev(self, x):
    if self.min is None or x <= self.max:
      return None
    elif x >= self.max:
      return self.max

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster and element_index > cluster.min:
      element_index = cluster.prev(element_index)
      return self.index(cluster_index, element_index)

    if cluster is None or element_index <= cluster.min:
      cluster_index = self.summary.prev(cluster_index)
      element_index = self.clusters[cluster_index].max
      return self.index(cluster_index, element_index)


  def delete(self, x):
    if self.min is None or x < self.min:
      return
    if self._universe_order == 1:
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
  next_times = time_func(lambda: instance.next(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  prev_times = time_func(lambda: instance.prev(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  delete_times = time_func(lambda: instance.delete(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  print('Average insert time is ' + str(sum(insert_times)/len(insert_times)))
  print('Average next time is ' + str(sum(next_times)/len(next_times)))
  print('Average prev time is ' + str(sum(prev_times)/len(prev_times)))
  print('Average delete time is ' + str(sum(delete_times)/len(delete_times)))

def main():
  size = pow(2, 16)
  test_data_structure(BitArray(size))
  test_data_structure(VEB(size))

if __name__ == '__main__':
  main()
