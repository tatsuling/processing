#!/usr/bin/env python

from __future__ import print_function

import sys
import os
#import yaml


def err(*objs):
    print( *objs, file=sys.stderr )
    sys.stderr.flush()

try:
    from yaml import CLoader as Loader
except:
    from yaml import Loader

class Filters(object):
    def filter(self, stats, **kwargs):
        if isinstance(stats, dict):
            ret = self.do_filter( stats, **kwargs )
        else:
            ret = []
            for stat in stats:
                stat = self.do_filter(stat, **kwargs)
                if stat != None: ret.append( stat )
        return ret

    def do_filter(self, stats, **kwargs): pass

class TagFilter(Filters):
    def __init__(self, tag):
        self.tag = tag

    def do_filter(self, stat, **kwargs):
        if not stat['simulator']['tags']:
            return None

        if self.tag in stat['simulator']['tags']:
            return stat

class PathFilter(Filters):
    def __init__(self, path):
        self.path = path

    def do_filter(self, stat, **kwargs):
        Prefix = ['base_machine']
        node = stat['base_machine']
        for p in self.path:
            if p in node:
                Prefix.append( p )
                node = node[p]
            else:
                raise ValueError()
        if kwargs.get('valueOnly'):
            return node
        return { '.'.join(Prefix): node }

print('#name  active.mean active.samples  drowsy.mean drowsy.samples  powerdown.mean powerdown.samples  user.cycles  L2.read.hit L2.write.hit L2.read.miss L2.write.miss  total.cycles')
#histogram = open('histogram.csv', 'ab')
for fn in sys.argv[1:]:
    err("  Loading [%s]" % (fn,))
    with open(fn) as file:
        loader = Loader(file)
        stats = []
        while loader.check_data():
            stats.append( loader.get_data() )

        #filters = [ TagFilter('total') ]
        #for filter in filters:
            #stats = filter.filter(stats)

        if not stats: continue

        kernel = TagFilter('kernel').filter(stats)[0]
        user = TagFilter('user').filter(stats)[0]
        total = TagFilter('total').filter(stats)[0]

        L2 = PathFilter(['L2_0']).filter(total, valueOnly=True)

        user_cycles = reduce( lambda a, x: x if x > a else a,
            map(
                lambda x: PathFilter(['ooo_%d_%d'%(x,x), 'cycles']).filter(user, valueOnly=True),
                range(16)
            )
        )
        total_cycles = reduce( lambda a, x: x if x > a else a,
            map(
                lambda x: PathFilter(['ooo_%d_%d'%(x,x), 'cycles']).filter(total, valueOnly=True),
                range(16)
            )
        )
        ipc = map(
            lambda x: PathFilter(['ooo_%d_%d'%(x,x), 'thread0', 'commit', 'ipc']).filter(total, valueOnly=True),
            range(16)
        )

        print( '%s  %d %d  %d %d  %d %d  %d  %d %d %d %d  %d  %s  %s  %d %d' % (
            os.path.splitext( os.path.basename(file.name) )[0],
            L2['activeCycles']['mean'], L2['activeCycles']['number_of_samples'],
            L2['drowsyCycles']['mean'], L2['drowsyCycles']['number_of_samples'],
            L2['powerdownCycles']['mean'], L2['powerdownCycles']['number_of_samples'],
            user_cycles,
            L2['cpurequest']['count']['hit']['read']['hit'],
            L2['cpurequest']['count']['hit']['write']['hit'],
            L2['cpurequest']['count']['miss']['read'],
            L2['cpurequest']['count']['miss']['write'],
            total_cycles,
            " ".join( map( lambda x: repr(x), L2['blockAccessDistance']['samples'] ) ),
            #repr( max( instructions ) ),
            " ".join( map( lambda x: repr(x), ipc ) ),
            L2['predictionCorrect'],
            L2['predictionWrong'],
        ) )
