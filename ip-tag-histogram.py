#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import sys, os, time
from Scalable import Scalable
from ProgressUpdater import Percentage, Updater
#from itertools 

def main():
    field_translation = [
        lambda f: int(f),
        lambda f: int(f),
        lambda f: int(f),
        lambda f: f == '1',
        lambda f: int(f, 16),
        lambda f: int(f, 16),
        lambda f: f
    ]
    for fn in sys.argv[1:]:
        with open(fn, 'rb') as f:
            begin_time = time.time()
            updater = Updater( 
                lambda: '{0} -- {1}'.format(
                    Percentage( 100 * f.tell() / os.fstat(f.fileno()).st_size ),
                    Scalable( f.tell() / (time.time() - begin_time), 'B/s' )
                ),
                0.5 )
            tags = {}
            for line in f:
                fields_str = line.split()
                # fields = [ fn(field) for (field, fn) in zip(fields_str, field_translation) ]
                addr = int( fields_str[4], 16 )
                tag = addr & ~(64-1)
                isData = fields_str[3] == '1'
                rip = int(fields_str[5], 16) if isData else addr

                try:
                    tags[tag].add( rip )
                except:
                    rips = set()
                    rips.add( rip )
                    tags[tag] = rips
                    
                updater.update()
            updater.final()

            hist = {}
            for length in [ len(rips) for rips in tags.values() ]:
                try:
                    hist[length] += 1
                except:
                    hist[length] = 1

            for accesses, tags in hist.iteritems():
                print( accesses, tags )
                
                
if __name__ == '__main__':
    main()

