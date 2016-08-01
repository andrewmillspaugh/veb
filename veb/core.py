import sys
import math
import time
import random

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
    # bitwise check to ensure universe_size is a power of 2
    # TODO: use higher-order bits ceil(u/2) and floor(u/2) bits
    # instead of x/sqrt(U) and x mod sqrt(U) so that we can build
    # a VEB of any size
    if (universe_size & (universe_size - 1)) != 0:
      raise Exception('universe_size must be a power of 2!')
    self.universe_size = universe_size
    self.min = None
    self.max = None
    if universe_size > 2:
      self.clusters = [None] * self.high(self.universe_size)
      self.summary = None
  
  def __contains__(self, x):
    # the easy cases  
    if not self.min:
        return False
    elif self.min == x:
        return True

    high = self.high(x)
    low = self.low(x)
    if self.clusters[high] is None:
        return False
    else:
      return low in self.clusters[high]

  def floor(self, x):
    return int(math.floor(x // int(math.sqrt(self.universe_size))))

  def high(self, x):
    return x // int(math.sqrt(self.universe_size))

  def low(self, x):
    return x % int(math.sqrt(self.universe_size))

  def insert(self, x):
    # if nothing is stored in min, lazily store x in the min (as well as the max)
    if self.min == None:
      self.min = self.max = x
    # something is already in min, so we have to figure out where to put it and,
    # because we know that the cluster isnt empty, we also have to deal with max
    else:
      # the new x is smaller than the existing min, so we need to swap them
      if x < self.min:
        self.min, x = x, self.min
      # universe size is greater than two, so we need to generate the summaries
      if self.universe_size > 2:
        high = self.high(x)
        # we've never touched this cluster, so we need to actually put something there
        if not self.clusters[high]:
          # create a cluster of size sqrt(universe_size)
          self.clusters[high] = VEB(self.high(self.universe_size))
        if not self.summary:
          self.summary = VEB(self.high(self.universe_size))
        # this cluster doesn't have a min value, which means that the value we're currently
        # inserting must be the min value as well as the max value
        if not self.clusters[high].min:
          self.summary.insert(high)
          self.clusters[high].min = self.clusters[high].max = self.low(x)
        else:
          self.clusters[high].insert(self.low(x))
      if x > self.max:
        self.max = max
      # the new x is bigger than the existing min, so we can blindly set it
      if x > self.max:
        self.max = x

  def next(self, x):
    # this tree is empty, or x is the biggest in it
    if not self.min or x >= self.max:
      return None
    elif x <= self.min:
      return self.min

    high = self.high(x)
    low = self.low(x)
    floor = self.floor(x)
    cluster = self.clusters[floor]

    if not cluster or low >= cluster.max:
      return high + self.clusters[self.summary.next(floor)].min
    else:
      return high + self.clusters[floor].next(low)

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
  # prev_times = time_func(lambda: instance.prev(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  # delete_times = time_func(lambda: instance.delete(random.randint(0, pow(2, 16) - 1)), pow(2,15))
  print('Average insert time is ' + str(sum(insert_times)/len(insert_times)))
  print('Average next time is ' + str(sum(next_times)/len(next_times)))
  # print('Average prev time is ' + str(sum(prev_times)/len(prev_times)))
  # print('Average delete time is ' + str(sum(delete_times)/len(delete_times)))

def main():
  #size = pow(2, 16)
  #test_data_structure(BitArray(size))
  #test_data_structure(VEB(size))
  baby_veb = VEB(64)
  baby_veb.insert(3)
  baby_veb.insert(9)
  baby_veb.insert(37)
  print(3 in baby_veb)
  print(9 in baby_veb)
  print(37 in baby_veb)
  print(2 not in baby_veb)
  print(10 not in baby_veb)
  print(36 not in baby_veb)

if __name__ == '__main__':
  main()
