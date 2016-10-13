#!/usr/bin/env python

import units

@units.unit
@units.symbol('cycles')
class cycles(units.Unit):
    pass


@units.unit
@units.symbol('subarray')
class subarray(units.Unit):
    pass


@units.unit
@units.symbol('byte')
class byte(units.Unit):
    pass


@units.unit
@units.symbol('line')
class line(units.Unit):
    pass
