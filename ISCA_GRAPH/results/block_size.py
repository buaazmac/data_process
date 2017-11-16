with open('overall_new.txt') as f:
	results = {}
	for app in ['bfs', 'sssp', 'pr']:
		results[app] = {}
		for graph in ['am', 'tw', 'wiki', 'pokec', 'lj', 'u', 'g']:
			results[app][graph] = {}
			for n_rows in [256, 512, 1024, 2048, 4096]:
				results[app][graph][n_rows] = {}
				for s_buffer in [0, 32, 256]:
					results[app][graph][n_rows][s_buffer] = {}
	for line in f:
		if 'Application' in line:
			continue
		arr = line.strip().split()
		app = arr[0]
		graph = arr[1].strip().split('-')[0]
		n_rows = int(arr[1].strip().split('-')[1])
		s_buffer = int(arr[1].strip().split('-')[2])
		exe_time = float(arr[2])
		energy = float(arr[3])
		n_process = int(arr[4])
		n_reduce = int(arr[5])
		n_apply = int(arr[6])
		orig_lt = float(arr[7]) / 1000.0 / 3600.0 / 24.0
		opt_lt = float(arr[8]) / 1000.0 / 3600.0 / 24.0 * 5
		results[app][graph][n_rows][s_buffer]['time'] = exe_time
		results[app][graph][n_rows][s_buffer]['energy'] = energy
		results[app][graph][n_rows][s_buffer]['n_process'] = n_process
		results[app][graph][n_rows][s_buffer]['n_reduce'] = n_reduce
		results[app][graph][n_rows][s_buffer]['n_apply'] = n_apply
		results[app][graph][n_rows][s_buffer]['orig_lt'] = orig_lt
		results[app][graph][n_rows][s_buffer]['opt_lt'] = opt_lt
	with open('block_size.csv', 'w') as wf:
		for app in ['bfs', 'sssp', 'pr']:
			wf.write(app + '\tGraph\t64KB\t\t128KB\t\t256KB\t\t512KB\t\t1MB\n\t')
			for i in [1,2,3,4,5]:
				wf.write('\tt(ms)\te(uJ)')
			wf.write('\n')
			for graph in ['am', 'tw', 'wiki', 'pokec', 'lj', 'u', 'g']:
				wf.write('\t' + graph)
				for n_rows in [256, 512, 1024, 2048, 4096]:
					wf.write('\t%.2f\t%.2f' % \
						(results[app][graph][n_rows][256]['time'],\
						 results[app][graph][n_rows][256]['energy']))
				wf.write('\n')
			wf.write('\n')
	with open('block_num.csv', 'w') as wf:
		wf.write('Graph\t64KB\t\t\t128KB\t\t\t256KB\t\t\t512KB\t\t\t1MB\n')
		for i in [1,2,3,4,5]:
			wf.write('\t#P\t#R\t#A')
		wf.write('\n')
		for graph in ['am', 'tw', 'wiki', 'pokec', 'lj', 'u', 'g']:
			wf.write(graph)
			for n_rows in [256, 512, 1024, 2048, 4096]:
				wf.write('\t%d\t%d\t%d' % \
					(results['bfs'][graph][n_rows][256]['n_process'], \
					 results['bfs'][graph][n_rows][256]['n_reduce'], \
					 results['bfs'][graph][n_rows][256]['n_apply']))
			wf.write('\n')
		wf.write('\n')
	with open('endurance.csv', 'w') as wf:
		wf.write('Application\tAmazon\t\tTwitter\t\tWiki\t\tPokec\t\tLJournal\t\tUniform\t\tG500\n')
		for app in ['bfs', 'sssp', 'pr']:
			wf.write(app)
			for graph in ['am', 'tw', 'wiki', 'pokec', 'lj', 'u', 'g']:
				wf.write('\t%.2f\t%.2f' % \
					(results[app][graph][256][256]['orig_lt'],\
					 results[app][graph][256][256]['opt_lt']))
			wf.write('\n')
	with open('buffer.csv', 'w') as wf:
		wf.write('Application\tAmazon\t\tTwitter\t\tWiki\t\tPokec\t\tLJournal\t\tUniform\t\tG500\n')
		for app in ['bfs', 'sssp', 'pr']:
			wf.write(app)
			for graph in ['am', 'tw', 'wiki', 'pokec', 'lj', 'u', 'g']:
				wf.write('\t%.2f\t%.2f' % \
					(results[app][graph][256][0]['time'],\
					 results[app][graph][256][256]['time']))
			wf.write('\n')
