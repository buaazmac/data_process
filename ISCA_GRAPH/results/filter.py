import os
import sys

with open('overall.txt') as f:
  with open('overall_new.txt', 'w') as wf:
    first_line = False
    for line in f:
      if first_line == False:
        first_line = True
        wf.write(line)
        continue
      arr = line.split()
      if arr[7][0] == '.':
        arr[7] = arr[7][2:]
      if arr[8][0] == '.':
        arr[8] = arr[8][2:]
      wf.write('\t'.join(arr) + '\n')
