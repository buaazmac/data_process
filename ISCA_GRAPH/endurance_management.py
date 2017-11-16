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
      elif write_time_flag:
        write_time_flag = False
        dist_arr = line.strip().split(',')
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

def multikeysort(items, columns):
	from operator import itemgetter
	comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
	def comparer(left, right):
		for fn, mult in comparers:
			result = cmp(fn(left), fn(right))
			if result:
				return mult * result
		else:
			return 0
	return sorted(items, cmp=comparer)

# Here is the main function
if __name__ == '__main__':
  t_dir = os.path.abspath(sys.argv[1])
  o_dir = os.path.abspath(sys.argv[2])
  items = os.listdir(t_dir)
  orig_list = []
  for item in items:
    if item.endswith('.log') and 'lda' not in item:
      path = t_dir + '/' + item
      tmp_rst = extract_data(path, item)
      orig_list.append(tmp_rst)
  rst_list = multikeysort(orig_list, ['app', 'graph', 'n_rows', 's_buffer'])
  overall_rst = {}
  for app in ['bfs', 'sssp', 'pr']:
    overall_rst[app] = {}
    for graph in ['u', 'g', 'am', 'tw', 'lj', 'wiki', 'pokec']:
      overall_rst[app][graph] = {}
      for n_row in ['256', '512', '1024', '2048', '4096']:
        overall_rst[app][graph][n_row] = {}
        for mb in ['0', '32', '256']:
          overall_rst[app][graph][n_row][mb] = dict(exe_time = 0.0, energy = 0.0)
        
  for item in rst_list:
    config = item['config']
    app = item['app']
    graph = item['graph']
    pr = item['n_rows']
    mb = item['s_buffer']
    result = item['data']

    overall_rst[app][graph][pr][mb]['exe_time'] = result['exe_time']
    overall_rst[app][graph][pr][mb]['energy'] = result['energy']
    overall_rst[app][graph][pr][mb]['n_process'] = result['n_process']
    overall_rst[app][graph][pr][mb]['n_reduce'] = result['n_reduce']
    overall_rst[app][graph][pr][mb]['n_apply'] = result['n_apply']
    overall_rst[app][graph][pr][mb]['b_orig_lt'] = result['b_orig_lt']
    overall_rst[app][graph][pr][mb]['b_opt_lt'] = result['b_opt_lt']
    overall_rst[app][graph][pr][mb]['orig_lt'] = result['orig_lt']
    overall_rst[app][graph][pr][mb]['opt_lt'] = result['opt_lt']
  overall_file = o_dir + 'overall.txt'
  time_file = o_dir + 'time.csv'
  energy_file = o_dir + 'energy.csv'
  block_file = o_dir + 'blocks.csv'
  endurance_file = o_dir + 'endurance.csv'
  with open(overall_file, 'w') as f:
    f.write('Application\tConfig\tExeTime\tEnergy\t#Process\t#Reduce\t#Apply\tOrigLT\tOptLT\n')
    for result in rst_list:
      f.write('%s\t%s\t%.2f\t%.2f\t%d\t%d\t%d\t%.2f\t%.2%f\n' % (result['app'], result['config'], result['data']['exe_time'], result['data']['energy'], result['data']['n_process'], result['data']['n_reduce'], result['data']['n_apply'], result['data']['orig_lt'], result['data']['opt_lt']))

