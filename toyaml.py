#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import yaml
import re
import math
from copy import deepcopy
from pprint import pformat

from units import watt, joule, second, hertz, volt, second
from sim_units import *
import units
import argparse


mW = watt(1e-3)


class Lambda(object):
    def __init__(self, params, f):
        self._params = params
        self._f = f
    def __repr__(self):
        return 'lambda {0}: {1}'.format(self._params, self._f)

def floor(x):
    if isinstance(x, units.Unit):
        return units.Unit(int(math.floor(x.Value)), x.Units)
    else:
        return int(math.floor(x))

def ceil(x):
    if isinstance(x, units.Unit):
        return units.Unit(int(math.ceil(x.Value)), x.Units)
    else:
        return int(math.ceil(x))

freq = cycles(2.4e9) / units.second(1)

params = {
    'SIZE': ('all', re.compile(r'\s*Total cache size.*: (\d+)'), [int, str]),
    'LINE_SIZE': ('all', re.compile(r'\s*Block size.*: (\d+)'), [int]),
    'ASSOC': ('all', re.compile(r'\s*Associativity.*: (\d+)'), [int]),
    'LATENCY': ('all', re.compile(r'\s*Access time.*: (\d*\.\d+)'), [
        float, 
        lambda x: x*second(1e-9), 
        lambda x: ceil(x*freq).Value]),
    'READ_PORTS': ('all', re.compile(r'\s*Read ports.*: (\d+)'), [int]),
    'WRITE_PORTS': ('all', re.compile(r'\s*Write ports.*: (\d+)'), [int]),
    'WAKE_LATENCY': ('all', re.compile(r'\s*Power gating Wakeup Latency.*: (\d*\.\d+)'), [
        float, 
        lambda x: x*second(1e-9), 
        lambda x: ceil(x*freq).Value]),
}

energy_data = {
    'size': ('all', re.compile(r'\s*Total cache size.*: (\d+)'), [int, lambda x: byte(x)]),
    'line_size': ('all', re.compile(r'\s*Block size.*: (\d+)'), [int, lambda x: byte(x)/line(1)]),
    'associativity': ('all', re.compile(r'\s*Associativity.*: (\d+)'), [int, lambda x:line(x)]),
    'banks': ('all', re.compile(r'\s*Number of banks.*: (\d+)'), [int]),

    'Ndwl': ('all', re.compile(r'\s*Best Ndwl.*: (\d+)'), [int]),
    'Ndbl': ('all', re.compile(r'\s*Best Ndbl.*: (\d+)'), [int]),

    'Vdd': ('all', re.compile(r'\s*Vdd.*=.*(\d*\.\d+)'), [float, lambda x:volt(x)]),
    'Vth': ('all', re.compile(r'\s*Vth.*=.*(\d*\.\d+)'), [float, lambda x:volt(x)]),

    'leakage_on': ('data', re.compile(r'\s*Total leakage power of a bank without power gating, including its network outside.*: (\d*\.\d+)'), [float, lambda x: x*mW]),
    'leakage_drowsy': ('data', re.compile(r'\s*Total leakage power of a bank, power gated with retaining memory content, including its network outside.*: (\d*\.\d+)'), [float, lambda x: watt(x*1e-3)]),

    # factor of 34 is from GatedVdd: A Circuit Technique to Reduce 
    # Leakage in Deep-Submicron Cache Memories -- Table 1
    'leakage_off': ('data', re.compile(r'\s*Total leakage power of a bank without power gating, including its network outside.*: (\d*\.\d+)'), [float, lambda x: x/34*mW]),

    'transition_drowsy_on': ('all', re.compile(r'\s*Power gating Wakeup Energy.*: (\d*\.\d+)'), [float, lambda x: joule(x*1e-9)/subarray(1)]),
}

def main():
    parser = argparse.ArgumentParser(description='Generate configurations')

    parser.add_argument('-b', '--base', dest='base', required=True, type=argparse.FileType('r'))
    parser.add_argument('-c', '--config', dest='config_file', required=True, type=argparse.FileType('w'))
    parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
    args = parser.parse_args()

    configuration = yaml.load(args.base)

    memory_configs = []
    energy_configs = {}

    print('import units')
    print('import sim_units')
    # print('cache_configuration = {')

    for f in args.infile:
        fn = f.name
        config_name = os.path.basename(fn).split('.')[0]
        memory_configs.append(config_name)
        # print 'config_name: ',config_name

        config = {}
        energy = {}
        section = 'all'
        for file_line in f:
            if re.match('.*Data array:', file_line):
                section = 'data'
            if re.match('.*Tag array:', file_line):
                section = 'tag'

            for name, (where,expr,convs) in params.items():
                if where != section: continue
                m = expr.match(file_line)
                if m:
                    v = m.group(1)
                    for conv in convs:
                        v = conv(v)
                    config[name] = v

            for name, (where,expr,convs) in energy_data.items():
                if where != section: continue
                m = expr.match(file_line)
                if m:
                    v = m.group(1)
                    for conv in convs:
                        v = conv(v)
                    energy[name] = v

        # wakeup energy = 1.13827 nJ
        # Vdd low = 0.6
        # Vdd high = 0.9
        # Energy to charge = C * dV * dV
        # 1.13827e-9 J / (0.3 V * 0.3 V ) = 1.264744e-8 C
        # Power line capacitance = 1.264744e-8 C

        # off to on energy = C * dV * dV
        # = 1.264744e-8 C * 0.9 V * 0.9 V
        # = 10.2 nJ

        # print('config:', pformat(config))
        # print('energy:', pformat(energy))

        energy['lines']     = energy['size'] / energy['line_size']
        energy['sets']      = energy['size'] / energy['line_size'] / energy['associativity']
        energy['subarray']  = subarray(energy['Ndwl'] * energy['Ndbl'])
        energy['mat']       = energy['Ndwl'] * energy['Ndbl'] / 4
        energy['lines/subarray'] = energy['lines'] / energy['subarray']

        energy['transition_drowsy_on'] = energy['transition_drowsy_on'] / energy['lines/subarray']

        vdd_high = energy['Vdd']
        vdd_low = volt(0.6)
        energy_from_drowsy = energy['transition_drowsy_on']
        power_capacitance = energy_from_drowsy / ( vdd_high - vdd_low ) ** 2

        energy['transition_gated_on'] = power_capacitance * vdd_high ** 2
        energy['leakage_on'] = energy['leakage_on'] / energy['lines']
        energy['leakage_drowsy'] = energy['leakage_drowsy'] / energy['lines']
        energy['leakage_off'] = energy['leakage_off'] / energy['lines']

        # print(pformat(energy, indent=4), ',')
        
        configuration['cache'][config_name] = {'base': 'wb_cache', 'params': config}
        energy_configs[config_name] = energy
    print('cache_configuration =', pformat(energy_configs))

    # sys.exit(1)

    for memory in memory_configs:
        energy = energy_configs[memory]

        name = 's_{0}'.format(memory)
        machine = deepcopy(configuration['machine']['base'])
        machine['description'] = 'Standard {0}'.format(memory)
        machine['caches'].append({'type': memory, 'name_prefix': 'L2_', 'insts': 1})
        configuration['machine'][name] = machine

        name = 'd_{0}'.format(memory)
        machine = deepcopy(configuration['machine']['base'])
        machine['description'] = 'Drowsy {0}'.format(memory)
        machine['caches'].append({'type': memory, 'name_prefix': 'L2_', 'insts': 1, 'option': {'drowsy': True}})
        configuration['machine'][name] = machine

        name = 'g_{0}'.format(memory)
        machine = deepcopy(configuration['machine']['base'])
        machine['description'] = 'Drowsy {0}'.format(memory)
        machine['caches'].append({'type': memory, 'name_prefix': 'L2_', 'insts': 1, 'option': {'gated_vdd': True}})
        configuration['machine'][name] = machine
        
        name = 'b_{0}'.format(memory)
        machine = deepcopy(configuration['machine']['base'])
        machine['description'] = 'Drowsy {0}'.format(memory)

        # betDrowsy = E(lp, on) / (P(on) - P(lp) ) * freq
        # betOff = E(gated, lp) / (P(lp) - P(gated) ) * freq

        leakage_saving_drowsy_on = energy['leakage_on'] - energy['leakage_drowsy']
        betDrowsy = energy['transition_drowsy_on'] / leakage_saving_drowsy_on * freq
        # print('transition_drowsy_on={0}'.format(transition_drowsy_on))
        # print('leakage_saving_drowsy_on={0}'.format(leakage_saving_drowsy_on))
        # print('betDrowsy={0}'.format(betDrowsy))

        transition_on_gated = joule(2.045e-9) / line(1)
        leakage_saving_gated_on = energy['leakage_on'] - energy['leakage_off']
        leakage_saving_gated_drowsy = energy['leakage_drowsy'] - energy['leakage_off']
        betGated = max(
            (transition_on_gated+energy['transition_gated_on']) / leakage_saving_gated_on * freq,
            (transition_on_gated+energy['transition_gated_on']) / leakage_saving_gated_drowsy * freq)

        # print('transition_gated_on={0}'.format(transition_gated_on))
        # print('leakage_saving_gated_on={0}'.format(leakage_saving_gated_on))
        # print('betGated={0}'.format(betGated))

        options = {'prediction': True, 
                   'betDrowsy': ceil(betDrowsy.Value), 
                   'betOff': ceil(betGated.Value), 
                   'onCutoff': ceil(betDrowsy.Value), 
                   'drowsyCutoff': ceil(betGated.Value)}
        machine['caches'].append({'type': memory, 'name_prefix': 'L2_', 'insts': 1, 'option': options})
        configuration['machine'][name] = machine
        
    del configuration['machine']['base']

    print(yaml.dump(configuration), file=args.config_file)

if __name__ == '__main__':
    main()

