#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import re
import getopt, sys
import time, os, math

from Scalable import Scalable
from ProgressUpdater import Percentage, ProgressUpdater

l2_re = re.compile('^L2_0:')
#option_re = re.compile('(?P<name>[a-zA-Z\-]+)\[(?P<value>[^\]]*)\]')
option_re = re.compile('([a-zA-Z\-]+)\[([^\]]*)\]')
options_to_output = [ 'core', 'init-cycle', 'sim-cycle', 'isData', 'address', 'ownerRIP', 'op-type' ]
#options_to_output = [ 'core', 'address', 'init-cycle', 'op-type', 'isData', 'ownerRIP', 'sim-cycle' ]


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:", ['output='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print( str(err) ) # will print something like "option -a not recognized"
        sys.exit(2)
    output = None
    for o, a in opts:
        if o in ("-o", "--output"):
            output = a
        else:
            assert False, "unhandled option"
    if output is None:
        sys.exit(1)

    with open(output, 'wb') as of:
        base_option_re_format = '{0}\[([^\]]*)\]'
        options_to_find_re = [ re.compile( base_option_re_format.format(option) ) for option in options_to_output ]
        for fn in args:
            with open(fn, 'rb') as f:
                begin_time = time.time()
                now = time.time()
                lineno = 0
                update_line = Updater( 
                    lambda: '{0} -- {1} -- {2}'.format( 
                        Percentage( 100 * f.tell() / os.fstat(f.fileno()).st_size ),
                        Scalable( f.tell() / (now - begin_time), 'B/s' ),
                        Scalable( lineno / (now - begin_time), 'lines/s' ) 
                    ),
                    0.5 )

                for line in f:
                    lineno += 1
                    if l2_re.match(line):
                        options = [ option_re.search(line).group(1) for option_re in options_to_find_re ]
                        # print( ' '.join( option.group(1) for option in options ), file=of )
                        print( ' '.join( options ), file=of )

                        now = time.time()
                        update_line.update()
                update_line.final()

if __name__ == '__main__':
    main()

