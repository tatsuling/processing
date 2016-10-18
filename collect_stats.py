#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import sys, os, time

from utility.ProgressUpdater import Updater, Percentage
from utility.Scalable import Scalable

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


def file_size(f):
    try:
        return f.size
    except:
        return os.fstat(f.fileno()).st_size

import threading
from multiprocessing import Process, Queue, Lock, BoundedSemaphore

def updater(finished_event, file, q, pid):
    while not finished_event.is_set():
        finished_event.wait(0.1)
        q.put( (pid, 'tell', file.tell()) )

def load_yaml(fn, q, pid, output_lock, semp):

    # output_lock.acquire()
    # print('load_yaml({0}, {1}, {2})'.format(fn, q, pid))
    # output_lock.release()

    with open(fn) as file:
        q.put( (pid, 'size', file_size(file)) )

        semp.acquire()

        finished = threading.Event()
        update_thread = threading.Thread(target=updater, args=(finished, file, q, pid))
        update_thread.daemon = True
        update_thread.start()

        loader = Loader(file)
        stats = []
        while loader.check_data():
            stats.append( loader.get_data() )

        semp.release()

        finished.set()
        update_thread.join()

    q.put( (pid, 'done', stats) )
    

q = Queue()
l = Lock()
semp = BoundedSemaphore(50)
procs = [Process(target=load_yaml, args=(fn, q, fn, l, semp)) for fn in sys.argv[1:]]
for proc in procs:
    proc.start()
progress = {}

begin = time.time()
progress_updater = Updater(lambda: ' {0}/{1}  {2}  {3}'.format(
    len([True for key,x in progress.items() if x.has_key('result')]),
    len([True for key,x in progress.items()]),
    Percentage( 
        sum([x.get('tell', 0) for key,x in progress.items()]) / 
        sum([x.get('size', 0) for key,x in progress.items()]) * 100 ) 
        if sum([x.get('size', 0) for key,x in progress.items()]) > 0 
        else '???',
    Scalable( sum([x.get('tell', 0) for key,x in progress.items()]) / (time.time() - begin), 'Bps', base=2 )
    ),
    0.25
)
    
#     updater = Updater(lambda: '  Loading [{0}] ({1}) {2}'.format(
#             file.name,
#             f_size,
#             Percentage(file.tell()/f_size*100 if f_size > 0 else '???' )
#         ), 
#         0.0)

while True:
    # alive = [proc for proc in procs if proc.is_alive()]
    # if len(alive) < 20:
    #     not_started = [proc for proc in procs if not proc.is_alive() and proc.exitcode is None]
    #     if len(not_started) > 0:
    #         not_started[0].start()
    try:
        pid,command,arg = q.get(timeout=0.1)
        if command == 'size':
            progress[pid] = {'size': arg}
        elif command == 'done':
            progress[pid]['result'] = arg
        elif command == 'tell':
            progress[pid]['tell'] = arg
    except:
        pass

    progress_updater.update()
    if not any(proc.is_alive() for proc in procs):
        break
progress_updater.final()

for fn,p in sorted(progress.items(), key=lambda x: x[0]):
    stats = p['result']
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
        os.path.splitext( os.path.basename(fn) )[0],
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

sys.exit(0)

for fn in sys.argv[1:]:
    p = Process(target=load_yaml, args=(fn, q, fn))

    f_size = os.path.getsize(fn)
    # err("  Loading [%s] (%d)" % (fn,f_size))
    with open(fn) as file:

        finished = threading.Event()
        update_thread = threading.Thread(target=updater, args=(finished, file, file_size(file)))
        update_thread.daemon = True
        update_thread.start()
        
        loader = Loader(file)
        stats = []
        while loader.check_data():
            stats.append( loader.get_data() )

        finished.set()
        update_thread.join()

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
