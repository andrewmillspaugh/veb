import sys
import math
import time
import random
from collections import defaultdict

class VEB(object):
  def __init__(self, word_size):
    self.min = self.max = None
    self.word_size = word_size
    self._summary_size = int(math.ceil(self.word_size / 2))
    self._universe_size = pow(2, self.word_size)
    self._num_clusters = 1 << self._summary_size
    if self.word_size > 1:
      #self.clusters = defaultdict(lambda: None)
      self.clusters = [None] * self._num_clusters
      self.summary = VEB(self._summary_size)
    else:
      self.clusters = None
      self.summary = None

  def __contains__(self, x):
    # the easy cases
    if self.min is None:
      return False
    elif self.min == x:
      return True
    elif x > self._universe_size - 1:
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
    return x >> int(self._summary_size)

  def low(self, x):
    return x & ( (1 << int(self._summary_size)) - 1)

  def index(self, i, j):
    return i * self._summary_size + j

  def member(self, x):
    if x == self.min or x == self.max:
      return True
    elif self.word_size == 1:
      return False
    else:
      cluster = self.clusters[self.high(x)]
      if cluster != None:
        return cluster.member(self.low(x))
      else:
        return False

  def __str__(self):
    string = ''
    if self.summary:
      string += self.summary.__str__()

    string += '\n(U = {})'.format(self._universe_size)

    if self.clusters:
      string += '\n'
      for index in range(0, len(self.clusters)):
        if self.clusters[index] is None:
          string += '[EMPTY]'
        else:
          string += self.clusters[index].__str__().replace('\n', '')

    return string

    template = '-'.join('{' + str(x) + '}' for x in range(self.universe_size))
    for element in iter(self):
      template = template.format(element = 1)
    return template
    # if self.clusters is None:
      # return summary
    # for cluster in range(0, len(self.clusters)):
      # summary += '['
      # for element in range(0, self.cluster_size):
        # if self.member(cluster * self.cluster_size + element):
          # summary += '1'
        # else:
          # summary += '0'
      # summary += ']'
    # return self.summary.__str__() + '\n' + summary

  def insert(self, x):
    if x > self._universe_size - 1:
      raise Exception('Cannot insert {}'.format(x))
    if self.min is None:
      self.min = self.max = x
      return

    if x == self.min:
      return
    if x < self.min:
      self.min, x = x, self.min
    if x > self.max:
      self.max = x

    if self.word_size == 1:
      return

    cluster_index = self.high(x)
    element_index = self.low(x)
    cluster = self.clusters[cluster_index]

    if cluster is None:
      cluster = self.clusters[cluster_index] = VEB(self._summary_size)

    if cluster.min is None:
      self.summary.insert(cluster_index)

    cluster.insert(element_index)

  def successor(self, x):
    if self.word_size == 1:
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
    if self.word_size <= 1:
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

def main():
  #size = pow(2, 16)
  #test_data_structure(VEB(size))

  veb = VEB(6)
  veb.insert(0)
  veb.insert(1)
  veb.insert(2)
  veb.insert(3)
  veb.insert(4)
  veb.insert(5)
  print('after 0 comes {}'.format(veb.successor(0)))
  print('after 1 comes {}'.format(veb.successor(1)))
  print('after 2 comes {}'.format(veb.successor(2)))
  return

  for size in range(4, 175):
    print('testing size = {}'.format(size))
    for x in range(0, size):
      print('testing x = {}'.format(x))
      veb = VEB(size)
      veb.insert(x)
      for y in range(0, size):
        if x == y:
          assert(veb.member(y))
        else:
          assert(not veb.member(y))

  return
  print('veb is ')
  for x in range(0, 16):
    print('{} ? {}'.format(x, veb.member(x)))
  return

  values = [ random.randint(0, 16) for _ in range(8) ]
  for val in values:
    veb.insert(val)
  print('veb is ', list(veb))
  print('sorted is ', sorted(set(values)))
  assert(list(veb) == sorted(set(values)))

if __name__ == '__main__':
  main()
