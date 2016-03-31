#!/usr/bin/env python

from __future__ import division

import time, sys, math

class Percentage(object):
    """Class to format percentages nicely

    >>> Percentage(1)
      1.000%

    >>> Percentage(1.55555)
      1.556%

    >>> Percentage(-1)
      0.000%

    >>> Percentage(199)
    100.000%
    """
    def __init__(self, val, fmt = None):
        if 0 <= val and val <= 100:
            self.val = val
        elif val < 0:
            self.val = 0
        else:
            self.val = 100
        self.fmt = fmt if fmt else '%7.3f%%'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.fmt % self.val

    def bar(self, size):
        size -= 2
        completed = int(math.floor( self.val * size / 100 ))
        if completed == size:
            return '[' + '='*completed + ']'
        else:
            return '[' + '='*completed + '>' + ' '*(size-completed-1) + ']'

class Updater(object):
    def __init__(self, disp, frequency):
        self.disp = disp
        self.frequency = frequency
        self.update_time = time.time()

    def update(self):
        now = time.time()
        if now - self.update_time >= self.frequency:
            try:
                output_str = self.disp()
            except:
                output_str = self.disp
            sys.stdout.write( '\r' + output_str )
            sys.stdout.flush()
            self.update_time = now

    def final(self):
        now = time.time()
        try:
            output_str = self.disp()
        except:
            output_str = self.disp
        sys.stdout.write( '\r' + output_str + '\n' )
        sys.stdout.flush()
        self.update_time = now
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

