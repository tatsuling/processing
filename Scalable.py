#!/usr/bin/env python

from __future__ import division

class Scalable(object):
    def __init__(self, val, suffix, base=10):
        prefixes = { 
            2: { 0: '', 10: 'ki', 20: 'Mi', 30: 'Gi', 40: 'Ti' },
            10: { 0: '', 3: 'k', 6: 'M', 9: 'G', 12: 'T', -3: 'm', -6: 'u', -9: 'n', -12: 'p', -15: 'f' },
            }
        self.val = val
        self.suffix = suffix
        self.base = base
        self.prefixes = prefixes[base]

    def __str__(self):
        vals = [ ( self.val / pow(self.base, exponent), prefix) 
                    for (exponent, prefix) in self.prefixes.iteritems()
                    if pow(self.base,exponent) <= self.val and self.val < pow(self.base,exponent+3)]
        if len(vals) > 0:
            return '%0.2f %s%s' % ( vals[0][0], vals[0][1], self.suffix )
        else:
            return '%0.2f %s' % ( self.val, self.suffix )

