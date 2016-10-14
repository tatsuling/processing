#!/usr/bin/env python

from __future__ import print_function

import sys
import math
from collections import defaultdict
import code
from pprint import PrettyPrinter
import itertools

import units

import cacti

pp = PrettyPrinter(indent=4)
critical_z = {
	95: { 
		3: 1.15, 
		4: 1.48,
		5: 1.71,
		6: 1.89,
		7: 2.02,
		8: 2.13,
		9: 2.21,
	}
}
#critical_z = {3: 1.15, 4: 1.48 }

def natural_numbers():
	n = 0
	while True:
		yield n
		n += 1

def sqrt(v):
	if isinstance(v, units.Unit):
		return math.sqrt(v.Value)
	else:
		return math.sqrt(v)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def mean( obj ):
	return sum(obj) / float(len(obj))
def variance( obj ):
	if len(obj) < 2: return 0
	m = mean(obj)
	return sum( map( lambda v: (v-m)*(v-m), obj ) ) / float(len(obj)-1)
def stddev( obj ):
	return sqrt( variance(obj) )
def se_mean( obj ):
	return stddev(obj) / sqrt( len(obj) )

def find_outlier( obj ):
	n = len(obj)
	m = mean(obj)
	sd = stddev(obj)
	if sd == 0: return None

	if not n in critical_z[95].keys(): return None
	crit_z = critical_z[95][n]
	i = 0

	z = ( max(obj) - m ) / sd
	return max(obj) if z >= critical_z else None
	#for val in obj:
		#z = abs(val - m) / sd
		#if z >= critical_z: 
			#return i
		#i = i + 1
	#return None

def output_csv_table( out_file, data_table, keycolumns, sorter=None, columns=None, comment_header=False ):
	def output_csv_row( out_file, key, record, columns):
		#code.interact(local=locals())
		stat_record = []
		n_samples = len(record.values()[0])
		#for name, values in record.iteritems():
		for column_name in columns:
			values = record[ column_name ]
			stripped_values = [ x.Value if isinstance(x, units.Unit) else x for x in values ]
			stat_record.append( len(stripped_values) )
			stat_record.append( mean(stripped_values) )
			stat_record.append( se_mean(stripped_values) )
			# stat_record.append( stddev(stripped_values) )

		items = tuple(map( lambda x: str(x), key )) + (n_samples,) + tuple(stat_record)
		format = ' '.join( ['%s'] * len(key) )	\
			+ ' %d '			\
			+ ' '.join( ['%s'] * len(stat_record) )
			#+ ' '.join( ['%.17g'] * len(stat_record) )
		#code.interact(local=locals())
		print( format % items, file=out_file )
		print( '%s: %s' % (key, record.keys()) )
	
	#print( "fn: %s" % ( out_file.name, ) )
	#code.interact(local=locals())

	#column_order = data_table.values()[0].keys()

	columns = columns or data_table.values()[0].keys()
	data_headers = list(
		itertools.chain.from_iterable(
			( [name+'_count', name+'_mean', name+'_se'] for name in columns )
		)
	)
	
	print( ( '#' if comment_header else '' ) + ' '.join(keycolumns) + ' samples ' + ' '.join(data_headers), file=out_file )
	average_record = None
	for key in sorted(data_table.keys(), key=sorter):
		record = data_table[ key ]
		try:
			if key[0] == 'Average':
				average_record = key, record
				continue
		except: pass
		output_csv_row( out_file, key, record, columns )

	if average_record != None:
		key, record = average_record
		output_csv_row( out_file, key, record, columns )

def pivot_table( data_table, headings ):
	#code.interact(local=locals())
	ret = []
	return ret

def filter_record( record, filters ):
	ret = {}
	for filter in filters:
		filtered_values = map( lambda rec: filter['func'](rec), zip( *record) )
		ret[ filter['name'] ] = filtered_values
	return ret

def average_last( k ):
	return ( k[0] == 'Average', k )
	#return None if k == 'Average' else k
	

########################################################
# Frequency
f = units.hertz(2.4e9)

cache = cacti.cache_configuration['32M']

def e_read(r): return cache['dynamic']['r'] * r
def e_write(w): return cache['dynamic']['w'] * w

def seconds(cycles): return cycles / f

def e_active_leakage(cycles): return cache['leakage']['on'] * seconds(cycles)
def e_drowsy_leakage(cycles): return cache['leakage']['drowsy'] * seconds(cycles)
def e_off_leakage(cycles)   : return cache['leakage']['off'] * seconds(cycles)

def e_active_energy(r, w)   : return e_read(r) + e_write(w)
def e_drowsy_energy(n)      : return cache['transition']['drowsy'] * cache['subarray'] / cache['lines'] * cacti.line(n)
def e_off_energy(n)         : return cache['transition']['off'] * cacti.line(n)

def active_cycles(tc, am, asamp, dm, dsamp, om, osamp):
	return am * asamp / cache['lines'].Value	# Number of cycles the entire cache is on.
					# Include fractional cycles.
def drowsy_cycles(tc, am, asamp, dm, dsamp, om, osamp):
	return dm * dsamp / cache['lines'].Value
def off_cycles(tc, am, asamp, dm, dsamp, om, osamp):
	return om * osamp / cache['lines'].Value
def unknown_cycles(tc, am, asamp, dm, dsamp, om, osamp):
	return tc - ( am * asamp + dm * dsamp + om * osamp ) / cache['lines'].Value

e_unk_leakage = e_active_leakage

# Static energy
def e_leakage_energy(tc, am, asamp, dm, dsamp, om, osamp):
	return e_active_leakage( active_cycles(tc, am, asamp, dm, dsamp, om, osamp) ) \
	     + e_drowsy_leakage( drowsy_cycles(tc, am, asamp, dm, dsamp, om, osamp) ) \
	     + e_off_leakage   ( off_cycles   (tc, am, asamp, dm, dsamp, om, osamp) ) \
             + e_unk_leakage   ( unknown_cycles(tc, am, asamp, dm, dsamp, om, osamp) )

# Dynamic energy
def e_rw_energy(r, w, r_miss, w_miss):	# special case: if there are no read hits then assume all off samples are a read hit for energy calculations
	return e_active_energy(r+r_miss, w+w_miss)
def e_transition_energy(dsamp, osamp):
	return e_drowsy_energy(dsamp) + e_off_energy(osamp)
def e_dynamic_energy(am, asamp, dm, dsamp, om, osamp, r, w, r_miss, w_miss):
	return e_rw_energy(r, w, r_miss, w_miss) + e_transition_energy(dsamp, osamp)

# Total energy
def e_total(tc, am, asamp, dm, dsamp, om, osamp, r, w, r_miss, w_miss):
	return e_dynamic_energy(am, asamp, dm, dsamp, om, osamp, r, w, r_miss, w_miss) + \
		e_leakage_energy(tc, am, asamp, dm, dsamp, om, osamp)
########################################################


def graph1_energy_usage( data_table ):

	filters = (
		{ 
			'name': 'percent_leakage',
			'func': 
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_leakage_energy(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp) / \
				e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss) 
		},
		{ 
			'name': 'percent_dynamic',
			'func': 
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_rw_energy(r_hit, w_hit, r_miss, w_miss) / \
				e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss) 
		},
		{ 
			'name': 'percent_transition',
			'func': 
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_transition_energy(d_samp, o_samp) / \
				e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss) 
		},

		{ 
			'name': 'leakage_power', 
			'func': 
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_leakage_energy(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp) / seconds(tc) 
		},
		{
			'name': 'dynamic_power',
			'func':
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_rw_energy(r_hit, w_hit, r_miss, w_miss) / seconds(tc),
		},
		{
			'name': 'transition_power',
			'func':
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_transition_energy(d_samp, o_samp) / seconds(tc),
		},

		{ 
			'name': 'leakage_energy', 
			'func': 
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_leakage_energy(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp)
		},
		{
			'name': 'dynamic_energy',
			'func':
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_rw_energy(r_hit, w_hit, r_miss, w_miss)
		},
		{
			'name': 'transition_energy',
			'func':
			lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc):
				e_transition_energy(d_samp, o_samp)
		},
	)

	def machine_mapping( machine ):
		if machine[0] == 'standard': return 'S'
		if machine[0] == 'drowsy': return 'D'
		if machine[0] == 'gated': return 'G'
		if machine[0] == 'bayesian': return 'B'
		return 'Unknown'

	def machine_order( machine ):
		if machine == 'S': return 0
		if machine == 'D': return 1
		if machine == 'G': return 2
		if machine == 'B': return 3
		return 5

	global e_unk_leakage
	with open('eu.all.csv', 'wb') as all_output_file:
		average_data = {}

		benchmarks = set( x[0] for x in data_table.keys() )
		for exp_benchmark in sorted(benchmarks):
			filtered_data = {}
			for (benchmark, machine), record in data_table.iteritems():
				if benchmark != exp_benchmark: continue
				m = ( machine_mapping(machine), )

				if machine == 'bayesian_l2-average': continue
				if machine == 'bayesian_l2-iir': continue

				if machine[0] == "standard_l2": e_unk_leakage = e_active_leakage
				if machine[0] == "drowsy_l2": e_unk_leakage = e_drowsy_leakage
				if machine[0] == "gated_l2": e_unk_leakage = e_off_leakage
				if machine[0] == "bayesian_l2-average": e_unk_leakage = e_off_leakage
				if machine[0] == "bayesian_l2-iir": e_unk_leakage = e_off_leakage
				if machine[0] == "bayesian_l2-prev": e_unk_leakage = e_off_leakage
				print( 'machine=%r f=%r leak=%r' % ( machine, e_unk_leakage, e_unk_leakage(1000) ) )
				#code.interact(local=dict(itertools.chain(globals().iteritems(), locals().iteritems())))

				filtered_data[m] = filter_record( record[0:12], filters )
				if not average_data.has_key(m):
					average_data[m] = {}
				for name, values in filtered_data[m].iteritems():
					if not average_data[m].has_key( name ):
						average_data[m][name] = []
					average_data[m][name].extend( values )
				#code.interact(local=locals())

			#code.interact(local=locals())
			columns = ['percent_leakage', 'percent_dynamic', 'percent_transition', 
				'leakage_power', 'dynamic_power', 'transition_power',
				'leakage_energy', 'dynamic_energy', 'transition_energy' ]
			with open('eu.%s.csv' % exp_benchmark, 'wb') as output_file:
				output_csv_table( output_file, filtered_data, keycolumns=['machine'], columns=columns, sorter=lambda x: machine_order(x[0]) )
				print( '# %s' % ( exp_benchmark, ), file=all_output_file )
				output_csv_table( 
					all_output_file, 
					filtered_data, 
					keycolumns=['machine'], columns=columns, 
					sorter=lambda x: machine_order(x[0]),
					comment_header=True )
				print( '', file=all_output_file )
				print( '', file=all_output_file )

		with open('eu.Average.csv', 'wb') as output_file:
			output_csv_table( 
				output_file, 
				average_data, 
				keycolumns=['machine'], 
				columns=columns, 
				sorter=lambda x: machine_order(x[0]),
				comment_header=False )

		#code.interact(local=locals())
		print( '# Average', file=all_output_file )
		output_csv_table( 
			all_output_file, 
			average_data, 
			keycolumns=['machine'], 
			columns=columns, 
			sorter=lambda x: machine_order(x[0]),
			comment_header=True )

	machines = ( (m,c) for c in ['32M'] for m in ['standard', 'drowsy', 'gated', 'bayesian'] )
	for exp_machine in machines:
		filtered_data = {}
		for (benchmark, machine), record in data_table.iteritems():
			if machine != exp_machine: continue

			if machine[0] == "standard": e_unk_leakage = e_active_leakage
			if machine[0] == "drowsy": e_unk_leakage = e_drowsy_leakage
			if machine[0] == "gated": e_unk_leakage = e_off_leakage
			if machine[0] == "bayesian": e_unk_leakage = e_off_leakage
			filtered_data[ (benchmark,) ] = filter_record( record[0:12], filters )

		#pp.pprint(filtered_data)
		#code.interact(local=locals())
		if len(filtered_data) > 1:
			average_data = {}
			for data in filtered_data.values():
				for name, values in data.iteritems():
					if not average_data.has_key( name ):
						average_data[name] = []
					average_data[name].extend( values )
			filtered_data[ ('Average',) ] = average_data

		#code.interact(local=locals())
		columns = ['percent_leakage', 'percent_dynamic', 'percent_transition', 
			'leakage_power', 'dynamic_power', 'transition_power',
			'leakage_energy', 'dynamic_energy', 'transition_energy' ]
		with open('eu.%s.csv' % ('.'.join(exp_machine)), 'wb') as output_file:
			#output_csv_table( output_file, sorted(filtered_data.iteritems(), key=lambda k: average_last(k[0])) )
			output_csv_table( output_file, filtered_data, keycolumns=['benchmark'], columns=columns )

def graph2_performance( data_table ):
	filtered_data = {}
	ipc_data = {}
	edp_data = {}
	energy_data = {}
	prediction_rate_data = {}
	benchmarks = set( x[0] for x in data_table.keys() )
	#print( benchmarks )
	#code.interact(local=locals())
	power_filter = lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc): \
		e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss) / seconds(tc)
	edp = lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc): \
		e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss) * seconds(tc)
	energy = lambda (a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, uc, r_hit, w_hit, r_miss, w_miss, tc): \
		e_total(tc, a_mean, a_samp, d_mean, d_samp, o_mean, o_samp, r_hit, w_hit, r_miss, w_miss)
	prediction_rate = lambda (right, wrong): 100.0*right / (right + wrong)

	for benchmark in benchmarks:
		print( benchmark )

		global e_unk_leakage
		e_unk_leakage = e_active_leakage
		#code.interact(local=locals())
		m = ('standard', '32M')
		if not data_table[(benchmark, m)]: continue

		def pivot(row):
			p_cycles = row[11]
			p_ipc = [ sum(ipcs) for ipcs in zip( *row[44:60] ) ]
			p_power = [ power_filter(rec) for rec in zip( *row[0:12] ) ]
			p_edp = [ edp(rec) for rec in zip( *row[0:12] ) ]
			p_energy = [ energy(rec) for rec in zip( *row[0:12]) ]
			return (p_cycles, p_ipc, p_power, p_edp, p_energy)

		s_cycles, s_ipc, s_power, s_edp, s_energy = pivot(data_table[(benchmark, ('standard', '32M'))])
		d_cycles, d_ipc, d_power, d_edp, d_energy = pivot(data_table[(benchmark, ('drowsy', '32M'))])
		g_cycles, g_ipc, g_power, g_edp, g_energy = pivot(data_table[(benchmark, ('gated', '32M'))])
		b_cycles, b_ipc, b_power, b_edp, b_energy = pivot(data_table[(benchmark, ('bayesian', '32M'))])

		filtered_data[ (benchmark,) ] = {
			'standard': s_cycles, 
			'drowsy': d_cycles, 
			'gated': g_cycles, 
			'bayesian': b_cycles,
		}
		ipc_data[ (benchmark,) ] = {
			's_ipc': s_ipc,
			'd_ipc': d_ipc,
			'g_ipc': g_ipc,
			'b_ipc': b_ipc,
		}
		edp_data[ (benchmark,) ] = {
			's_edp': s_edp,
			'd_edp': d_edp,
			'g_edp': g_edp,
			'b_edp': b_edp,
		}
		energy_data[ (benchmark,) ] = {
			's_energy': s_energy,
			'd_energy': d_energy,
			'g_energy': g_energy,
			'b_energy': b_energy,
		}
# 		prediction_rate_data[ (benchmark,) ] = {
# 			'a_pred_correct': b_a_prediction_correct,
# 			'a_pred_wrong': b_a_prediction_wrong,
# 			'a_pred_rate': b_a_prediction_rate,
# 			'i_pred_correct': b_i_prediction_correct,
# 			'i_pred_wrong': b_i_prediction_wrong,
# 			'i_pred_rate': b_i_prediction_rate,
# 			'p_pred_correct': b_p_prediction_correct,
# 			'p_pred_wrong': b_p_prediction_wrong,
# 			'p_pred_rate': b_p_prediction_rate,
# 		}


	#print (filtered_data)
	#code.interact(local=locals())

	if len(filtered_data) > 1:
		average_data = {}
		for data in filtered_data.values():
			for name, values in data.iteritems():
				if not average_data.has_key( name ):
					average_data[name] = []
				average_data[name].extend( values )
		filtered_data[ ('Average',) ] = average_data
		#code.interact(local=locals())
	if len(ipc_data) > 1:
		average_data = {}
		for data in ipc_data.values():
			for name, values in data.iteritems():
				if not average_data.has_key( name ):
					average_data[name] = []
				average_data[name].extend( values )
		ipc_data[ ('Average',) ] = average_data
		#code.interact(local=locals())
	if len(edp_data) > 1:
		average_data = {}
		for data in edp_data.values():
			for name, values in data.iteritems():
				if not average_data.has_key( name ):
					average_data[name] = []
				average_data[name].extend( values )
		edp_data[ ('Average',) ] = average_data
		#code.interact(local=locals())
	if len(energy_data) > 1:
		average_data = {}
		for data in energy_data.values():
			for name, values in data.iteritems():
				if not average_data.has_key( name ):
					average_data[name] = []
				average_data[name].extend( values )
		energy_data[ ('Average',) ] = average_data
		#code.interact(local=locals())
# 	if len(prediction_rate_data) > 1:
# 		average_data = {}
# 		for data in prediction_rate_data.values():
# 			for name, values in data.iteritems():
# 				if not average_data.has_key( name ):
# 					average_data[name] = []
# 				average_data[name].extend( values )
# 		prediction_rate_data[ ('Average',) ] = average_data
# 		#code.interact(local=locals())

	#code.interact(local=locals())
	#pivot_table( sorted(filtered_data.iteritems(), key=lambda k:k[0]), ['benchmark', 'j'] )

	columns = ['standard', 'drowsy', 'gated', 'bayesian']
	with open('performance.csv', 'wb') as output_file:
		output_csv_table( output_file, filtered_data, keycolumns=['benchmark'], columns=columns )

	columns = ['s_ipc', 'd_ipc', 'g_ipc', 'b_ipc']
	with open('ipc.csv', 'wb') as output_file:
		output_csv_table( output_file, ipc_data, keycolumns=['benchmark'], columns=columns )

	columns = ['s_edp', 'd_edp', 'g_edp', 'b_edp']
	with open('edp.csv', 'wb') as output_file:
		output_csv_table( output_file, edp_data, keycolumns=['benchmark'], columns=columns )

	columns = ['s_energy', 'd_energy', 'g_energy', 'b_energy']
	with open('energy.csv', 'wb') as output_file:
		output_csv_table( output_file, energy_data, keycolumns=['benchmark'], columns=columns )

# 	columns = []
# 	columns.extend( ['a_pred_correct', 'a_pred_wrong', 'a_pred_rate'] )
# 	columns.extend( ['i_pred_correct', 'i_pred_wrong', 'i_pred_rate'] )
# 	columns.extend( ['p_pred_correct', 'p_pred_wrong', 'p_pred_rate'] )
# 	with open('prediction.csv', 'wb') as output_file:
# 		output_csv_table( output_file, prediction_rate_data, keycolumns=['benchmark'], columns=columns )


def graph3_histogram( data_table ):
	filtered_data = {}
	#benchmarks = set()
	benchmarks = set( x[0] for x in data_table.keys() if x[1] == ('standard','32M') )
	#code.interact(local=locals())
	for (benchmark, machine), record in data_table.iteritems():
		if machine != "standard_l2": continue

		#benchmarks.add( benchmark )
		accessDistance_histogram = record[12:44]
		totals = list( sum(x) for x in zip( *accessDistance_histogram ) )
		filtered_data[ benchmark ] = {}
		for idx, field in enumerate(accessDistance_histogram):
			filtered_data[benchmark][ (benchmark, 2**idx, idx) ] = { 
				'distance': [trial_value / trial_total for trial_value, trial_total in zip(field, totals)] 
			}

	for benchmark in benchmarks:
		with open('histogram.%s.csv' % (benchmark,), 'wb') as output_file:
			if benchmark not in filtered_data: continue
			output_csv_table( 
				output_file, 
				filtered_data[benchmark], 
				keycolumns=['benchmark', 'ii', 'i'],
				sorter=lambda v: v[2] )

columns = {
	'active_samples': 0,
	'active_mean': 1,
	'drowsy_samples': 2,
	'drowsy_mean': 3,
	'off_samples': 4,
	'off_mean': 5,
}

data = defaultdict( lambda: [] )
for fn in sys.argv[1:]:
	with open(fn) as file:
		for line in file:
			if line.strip()[0] == '#': continue

			record = map( lambda v: float(v) if is_number(v) else v, line.split() )

			id = record[0].split('.')
			benchmark = id[0]
			machine = tuple(id[2].split('_'))

			for idx, val in zip( natural_numbers(), record[1:] ):
				fields = data[(benchmark, machine)]
				try:
					fields[idx].append( val )
				except IndexError:
					fields.insert( idx, [val] )

			if machine[0] == 'gated':
				a_samp = fields[1][-1]
				fields[4] = fields[4][:-1] + [120]
				fields[5] = fields[5][:-1] + [a_samp]

			if machine[0] == 'bayesian':
				a_samp = fields[1][-1]
				d_samp = fields[3][-1]
				r_miss = fields[9][-1]
				w_miss = fields[10][-1]
				pred_samp = fields[61][-1]
				diff = r_miss + w_miss
				print( "%d %d %d %d" % (a_samp, d_samp, pred_samp, diff) )
				fields[4] = fields[4][:-1] + [611129]
				fields[5] = fields[5][:-1] + [diff]


graph1_energy_usage( data )
graph2_performance( data )
graph3_histogram( data )

