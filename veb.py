import sys
import time
import random

# O(1) insert/delete
# O(n) next/prev
class BitArray(object):
  def __init__(self, u = pow(2,16)):
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
  test_data_structure(BitArray())

if __name__ == '__main__':
  main()
