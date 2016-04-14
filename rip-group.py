#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import sys, os, time
from Scalable import Scalable
from ProgressUpdater import Percentage, Updater
import tarfile
from itertools import izip_longest
from multiprocessing import Pool,Process,Manager
#from itertools 

def file_size(f):
    try:
        return f.size
    except:
        return os.fstat(f.fileno()).st_size

def process_file(fn, f=None):
    f = f or open(fn, 'rb')
    begin_time = time.time()
    updater = Updater( 
        lambda: '{0} -- {1} -- {2}'.format(
            Percentage( 100 * f.tell() / file_size(f) ),
            Scalable( f.tell() / (time.time() - begin_time), 'B/s' ),
            fn
        ),
        0.5 )
    accesses = []
    cycles = []
    for line in f:
        fields = line.split()
        core = int( fields[0] )
        cycle = int( fields[2] )
        isData = fields[3] == '1'
        addr = int( fields[4], 16 )

        tag = addr & ~(64-1)
        rip = int(fields[5], 16) if isData else addr

        if not isData: continue

        # access = {'rip': rip, 'tag': tag, 'cycle': cycle, 'core': core}
        # accesses.append( access )
        cycles.append( cycle )

        updater.update()
    updater.final()

#     with open(fn+'.time.csv', 'wb') as of:
#         cycles = [ access['cycle'] for access in accesses ]
#         last_cycle = 0
#         for cycle in sorted( cycles ):
#             for i in xrange(last_cycle, cycle):
#                 print( '0', file=of )
#             print( '1', file=of )
#             last_cycle = cycle + 1

    f.close()
    return None

def main():
#    pool = Pool(8)
#    non_tarfiles = [ fn for fn in sys.argv[1:] if not tarfile.is_tarfile(fn) ]
#    tarfiles = [ fn for fn in sys.argv[1:] if tarfile.is_tarfile(fn) ]
#    file_rips = pool.map( process_file, non_tarfiles )
#    file_rips = zip(non_tarfiles, file_rips)

    file_rips = []
    for fn in sys.argv[1:]:
        if tarfile.is_tarfile(fn):
            tf = tarfile.open(fn)
            for ti in tf:
                if not ti.isfile(): continue
                f = tf.extractfile(ti)
                print( ti.name, 'is', Scalable(ti.size, 'bytes'), file=sys.stderr )
                file_rips.append( (ti.name, process_file(ti.name, f) ) )
                f.close()
            tf.close()
        else:
            with open(fn, 'rb') as f:
                file_rips.append( (fn, process_file(fn, f)) )

#    with open('freq.csv', 'wb') as of:
#        total = [ sum([len(tags) for rip,tags in rips]) for fn,rips in file_rips ]
#        total_rips = [ len(rips) for fn,rips in file_rips ]
#        for i,rips in enumerate( izip_longest( *[ rips for fn,rips in file_rips] ), start=1 ):
#            line = []
#            for j,rip_vals in enumerate( rips ):
#                if rip_vals is None:
#                    values = [None] * 2
#                elif 100*i/total_rips[j] > 80:
#                    values = [None] * 2
#                else:
#                    rip, tags = rip_vals
#                    values = [ 100*i/total_rips[j], 100*len(set(tags))/len(tags) ]
#                line.extend( values )
#            print( ' '.join( [ str(value) if value else '-' for value in line ] ), file=of )

#     with open('output.csv', 'wb') as of:
#         cumulative = [0] * len(file_rips)
#         total = [ sum([len(tags) for rip,tags in rips]) for fn,rips in file_rips ]
#         total_rips = [ len(rips) for fn,rips in file_rips ]
#         headers = []
#         for fn,rips in file_rips:
#             headers.extend( (fn+' rip %', fn+' tag %') )
#         print( ', '.join( headers ), file=of )
#         for i,rips in enumerate( izip_longest( *[ rips for fn,rips in file_rips] ), start=1 ):
#             line = []
#             for j,rip_vals in enumerate( rips ):
#                 if rip_vals is None:
#                     values = [None] * 2
#                 else:
#                     rip, tags = rip_vals
#                     cumulative[j] += len(tags)
#                     values = [ 100*i/total_rips[j], 100*cumulative[j]/total[j] ]
#                 line.extend( values )
#             print( ', '.join( [ str(value) if value else '' for value in line ] ), file=of )

if __name__ == '__main__':
    main()

