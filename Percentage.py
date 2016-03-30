#!/usr/bin/env python

from __future__ import division

import math

class Percentage(object):
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return '%8.3f%%' % self.val

    def bar(self, size):
        size -= 2
        completed = int(math.floor( self.val * size / 100 ))
        if completed == size:
            return '[' + '='*completed + ']'
        else:
            return '[' + '='*completed + '>' + ' '*(size-completed-1) + ']'

