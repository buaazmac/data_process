#!/bin/usr/python
import os
import sys
import os.path
import re

max_endurance = float(1e12)

def compute_row_endurance(exe_time, dist_arr, n_compute, compute_rows):
  if compute_rows == 0:
    max_w = max(dist_arr)
    orig_lt = exe_time * (max_endurance / float(max_w))
    return (orig_lt, orig_lt)
  orig_lt = (max_endurance / float(n_compute)) * exe_time
  n_rows = len(dist_arr)
  opt_ratio = float(n_rows) / float(compute_rows)
  opt_lt = orig_lt / opt_ratio
  return (orig_lt, opt_lt)

def compute_block_endurance(exe_time, lifetime_arr):
  remaining = [100.0 for x in range(len(lifetime_arr))]
  wear_speed = map(lambda x: 100.0 * float(exe_time) / float(x), lifetime_arr)
  wear_speed.sort(reverse=True)
  if len(remaining) != len(wear_speed):
    print 'Unmatched size of arrays!'
  orig_lt = min(lifetime_arr)
  current_min = 100.0
  exe_cnt = 0
  while current_min > 0:
    print 'Current iteration: ' + str(exe_cnt)
    exe_cnt += 1
    for i in xrange(len(remaining)):
      remaining[i] = remaining[i] - wear_speed[i]
    current_min = min(remaining)
    remaining[i].sort(reverse=False)
  return (orig_lt, exe_time * exe_cnt)

def extract_data(file_name):
  config_str = file_name.split('.')[0]
  config_arr = config_str.split('-')
  tag = config_arr[0] + '-' + config_arr[1] + '-' + config_arr[2]
  app = config_arr[3]
  graph = config_arr[4]
  pr = config_arr[5]
  mb = config_arr[6]
  n_process = 0
  n_reduce = 0
  n_apply = 0
  exe_time = 0.0
  energy = 0.0
  compute_rows = 30
  blocks_orig_lt = []
  blocks_opt_lt = []
  block_sum = 0
  block_flag = False
  write_time_flag = True
  n_compute = -1
  with open(file_name) as f:
    for line in f:
      if 'Process Blocks(' in line:
        n_process = int(line.split()[3][:-2])
        n_reduce = int(line.split())[7][:-2])
        n_apply = int(line.split())[11][:-2])
      elif 'Completion Time' in line:
        exe_time = float(line.strip().split()[-1]) / 1000000000000.0
      elif 'Energy Consumption' in line:
        energy = float(line.strip().split()[-1]) / 1000000000.0
      elif 'Block Summary' in line:
        block_sum += 1
      elif 'Total Write:' in line:
        avg_write = float(line.strip().split()[-1])
        if block_sum == 1:
          p_avg_write = avg_write
        elif block_sum == 2:
          r_avg_write = avg_write
        elif block_sim == 3:
          a_avg_write = avg_write
        elif 'Block#' in line:
          block_flag = True
        elif block_flag:
          block_flag = False
          arr = line.split(', ')
        elif 'Block#' in line:
          write_time_flag = True
          n_compute = int(line.strip().split()[-1])
        elif write_time_flag:
          write_time_flag = False
          dist_arr = line.strip().split(',')
          block_lt = compute_row_endurance(exe_time, dist_arr, n_compute, compute_rows)
          blocks_orig_lt.append(block_lt[0])
          blocks_opt_lt.append(block_lt[1])
  res = {}
