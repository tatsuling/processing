#!/usr/bin/env python

import utility.units

@utility.units.unit
@utility.units.symbol('cycles')
class cycles(utility.units.Unit):
    pass


@utility.units.unit
@utility.units.symbol('subarray')
class subarray(utility.units.Unit):
    pass


@utility.units.unit
@utility.units.symbol('byte')
class byte(utility.units.Unit):
    pass


@utility.units.unit
@utility.units.symbol('line')
class line(utility.units.Unit):
    pass
