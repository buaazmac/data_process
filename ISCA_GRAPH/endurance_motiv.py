#!/bin/usr/python
import os
import sys
import os.path
import re

max_endurance = float(1e12)

show_block = []
show_n_compute = -1

def compute_row_endurance(exe_time, dist_arr, n_compute, compute_rows):
  if compute_rows == 0:
    max_w = max(dist_arr)
    orig_lt = exe_time * (max_endurance / float(max_w))
    return (orig_lt, orig_lt)
  orig_lt = (max_endurance / float(n_compute)) * exe_time
  n_rows = len(dist_arr)
  opt_ratio = float(n_rows) / float(compute_rows)
  opt_lt = orig_lt * opt_ratio
  return (orig_lt, opt_lt)

def compute_block_endurance(exe_time, lifetime_arr):
  interval = 100000
  remaining = [100.0 for x in range(len(lifetime_arr))]
  wear_speed = map(lambda x: interval * 100.0 * float(exe_time) / float(x), lifetime_arr)
  wear_speed.sort(reverse=True)
  if len(remaining) != len(wear_speed):
    print 'Unmatched size of arrays!'
  orig_lt = min(lifetime_arr)
  return (orig_lt, 0)
  current_min = 100.0
  exe_cnt = 0
  while current_min > 0:
    for i in xrange(len(remaining)):
      remaining[i] = remaining[i] - wear_speed[i]
    current_min = min(remaining)
    remaining.sort(reverse=True)
    exe_cnt += 1
    exe_cnt += 1
  print orig_lt, exe_time * exe_cnt * interval
  return (orig_lt, exe_time * exe_cnt * interval)

def extract_data(file_path, file_name):
  global max_endurance, show_block, show_n_compute
  config_str = file_name.split('.')[0]
  config_arr = config_str.split('-')
  tag = config_arr[0] + '-' + config_arr[1] + '-' + config_arr[2]
  app = config_arr[3]
  graph = config_arr[4]
  pr = config_arr[5]
  mb = config_arr[6]
  config = graph + '-' + pr + '-' + mb
  n_process = 0
  n_reduce = 0
  n_apply = 0
  exe_time = 0.0
  energy = 0.0
  compute_rows = 30
  blocks_orig_lt = []
  blocks_opt_lt = []
  block_sum = 0
  write_time_flag = False
  n_compute = -1
  with open(file_path) as f:
    for line in f:
      if 'Process Blocks(' in line:
        n_process = int(line.split()[3][:-1])
        n_reduce = int(line.split()[7][:-1])
        n_apply = int(line.split()[11])
      elif 'Completion Time' in line:
        exe_time = float(line.strip().split()[-1]) / 1000000000.0
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
        elif block_sum == 3:
          a_avg_write = avg_write
      elif 'Block#' in line:
        write_time_flag = True
        n_compute = int(line.strip().split()[-1])
        if 'ReduceBlock' in line and show_n_compute == -1:
          show_n_compute = -2
      elif write_time_flag:
        write_time_flag = False
        dist_arr = line.strip().split(',')
        if show_n_compute == -2:
          show_n_compute = n_compute
          show_block = dist_arr
        block_lt = compute_row_endurance(exe_time, dist_arr, n_compute, compute_rows)
        if block_lt[1] < 1:
          print line, block_lt[1]
        blocks_orig_lt.append(block_lt[0])
        blocks_opt_lt.append(block_lt[1])
  print min(blocks_orig_lt), max(blocks_opt_lt)
  print min(blocks_opt_lt), max(blocks_opt_lt)
  overall_lt = compute_block_endurance(exe_time, blocks_opt_lt)
  res = {}
  data = {}
  data['n_process'] = n_process
  data['n_reduce'] = n_reduce
  data['n_apply'] = n_apply
  data['exe_time'] = exe_time
  data['energy'] = energy
  data['b_orig_lt'] = blocks_orig_lt
  data['b_opt_lt'] = blocks_opt_lt
  data['orig_lt'] = overall_lt[0]
  data['opt_lt'] = overall_lt[1]
  res['tag'] = tag
  res['app'] = app
  res['graph'] = graph
  res['n_rows'] = pr
  res['s_buffer'] = mb
  res['config'] = config
  res['data'] = data
  return res

# Here is the main function
if __name__ == '__main__':
  result = extract_data('./full/11-10-full-bfs-wiki-256-0.log', '11-10-full-bfs-wiki-256-0.log')
  show_block = map(lambda x: int(x), show_block)
  avg_lt = sum(show_block) / float(len(show_block))
  print 'Min: %d, Max: %d, Avg: %.2f, Compute: %d' % (min(show_block), max(show_block), avg_lt, show_n_compute)
  block_lt_dist = result['data']['b_orig_lt']
  avg_blt = sum(block_lt_dist) / float(len(block_lt_dist))
  with open('endurance_motive.csv', 'w') as f:
    f.write('Rows -- Min: %d, Max: %d, Avg: %.2f, Compute: %d\n' % (min(show_block), max(show_block), avg_lt, show_n_compute))
    f.write('Blocks -- Min: %d, Max: %d, Avg: %.2f\n' % (min(block_lt_dist), max(block_lt_dist), avg_blt))
    f.write('#Process: %d, #Reduce: %d, #Apply: %d\n' % (result['data']['n_process'], result['data']['n_reduce'], result['data']['n_apply']))
    num = 1
    for lt in block_lt_dist:
      f.write('%d\t%d\n' % (num, lt))
      num += 1
