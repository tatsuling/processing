#!/usr/bin/env python

from __future__ import division

import time, sys

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
        
