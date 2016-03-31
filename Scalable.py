#!/usr/bin/env python

from __future__ import division

class Scalable(object):
    """Return an object that can scale its output with SI prefixes.

    >>> Scalable(1, 'B/s')
    1.00 B/s

    >>> Scalable(2000, 'B/s')
    2.00 kB/s

    >>> Scalable(0.1, 'g')
    100.00 mg

    >>> Scalable(4e15, 'bps')
    4000.00 Tbps
    
    """
    def __init__(self, val, suffix, base=10):
        prefixes = { 
            2: { 0: '', 10: 'ki', 20: 'Mi', 30: 'Gi', 40: 'Ti' },
            10: { 0: '', 3: 'k', 6: 'M', 9: 'G', 12: 'T', -3: 'm', -6: 'u', -9: 'n', -12: 'p', -15: 'f' },
            }
        self.val = val
        self.suffix = suffix
        self.base = base
        self.prefixes = prefixes[base]

    def __repr__(self):
        return str(self)

    def __str__(self):
        vals = [ ( self.val / pow(self.base, exponent), exponent, prefix ) 
                    for (exponent, prefix) in self.prefixes.iteritems() 
                    if pow(self.base, exponent) <= self.val ]
        value, exponent, prefix = max( vals, key=lambda v: v[1] )
        try:
            return '%0.2f %s%s' % ( value, prefix, self.suffix )
        except:
            return '%0.2f %s' % ( self.val, self.suffix )

if __name__ == "__main__":
    import doctest
    doctest.testmod()

