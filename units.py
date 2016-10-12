#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from itertools import chain, izip, ifilter
#import functools

try:
    from functools import total_ordering
except:
    def total_ordering(cls):
        comparison = ['__lt__', '__gt__', '__le__', '__ge__']
        convertions =   [('__gt__', lambda self, other: not (self < other or self == other)),
                         ('__le__', lambda self, other: self < other or self == other),
                         ('__ge__', lambda self, other: not self < other)]
        roots = [ op for op in comparison if getattr(cls, op, None) is not getattr(object, op, None) ]
        if not roots:
            raise ValueError('must define < operator for total_ordering')
        for opname, opfunc in convertions:
            if opname not in roots:
                opfunc.__name__ = opname
                opfunc.__doc__ = getattr(int, opname).__doc__
                setattr(cls, opname, opfunc)
        return cls 


try:
    from collections import Counter
except:
    from Counter import Counter


def expandUnitList(units):
    try:
        ret = Counter()
        for u, c in Counter(units).iteritems():
            # print '*** expandUnitList : u=%s c=%s' % (u, c)
            ret.update(
                dict([(uu, c * cc) for uu, cc in u.base_units().iteritems()]))
        return ret
    except Exception as e:
        print 'Exception:'
        print type(e)
        print e.args
        print e
        print '--------------------------'
        return units.base_units()


def validSimplification(base, derived):
    # print 'valid?', base, derived

    paired_counts = ((base[unit], cnt)
                     for unit, cnt in derived.base_units().iteritems())
    moved_wrong = False if len(derived.base_units()) > 1 else True
    for b, c in paired_counts:
        if b == 0 and c != 0:
            return False
        # print b, c

        # Check if it is going to switch the exponent between top and bottom
        # and it goes to more than a single unit. (e.g. -2 -> 2 is invalid,
        # -2 -> 1 is valid)
        if b > 0 and c > 0 and (b - c) < -1:
            return False
        if b < 0 and c < 0 and (b - c) > 1:
            return False

        # if b > 0 and c < -1: return False
        # if b < 0 and c >  1: return False
        # if abs(c) == 1:
        if b > 0 and c > 0 and (b - c) < 0:
            if moved_wrong:
                return False
            moved_wrong = True
        if b < 0 and c < 0 and (b - c) > 0:
            if moved_wrong:
                return False
            moved_wrong = True
        if b > 0 and c < 0:
            if moved_wrong:
                return False
            moved_wrong = True
        if b < 0 and c > 0:
            if moved_wrong:
                return False
            moved_wrong = True
    return True


def simplify(units):
    # print 'simplify(%s)' % (units,)

    # Get the base units of all of the units in the argument
    try:
        units = units.base_units()
    except:
        units = expandUnitList(units)

    # print '-- ', units
    keys = [
        # Maximum of upper exponents minus lower exponents
        # Prefer conversions that result in more upper exponents and fewer
        # lower
        lambda d: -sum(units[u] - c for u, c in d.base_units().iteritems()),

        # Minimum number in the exponents
        lambda d: sum(abs(units[u] - c)
                      for u, c in d.base_units().iteritems()),

        # Count number of times a simplification can be applied
        lambda d: - \
        min(units[u] / c for u, c in d.base_units().iteritems()
            if abs(units[u]) >= abs(c) and c != 0),

        # Largest number of changed units
        lambda d: -len(d.base_units())
    ]

    valid = list(derivedUnits)

    while True:
        valid = [d for d in valid if validSimplification(units, d)]
        # print 'valid list:', list(valid)

        if not any(valid):
            break

        for f in keys:
            valid = sorted(valid, key=f)

        conversion = valid[0]
        # print '\tconversion: ', conversion
#        print '\tcombining...'
        while validSimplification(units, conversion):
            units.subtract(conversion.base_units())
            units.update([conversion])
        # print '\t-- ', units

#    print [u for u, c in units.iteritems() if c == 0]
    for u in [u for u, c in units.iteritems() if c == 0]:
        del units[u]
#    print units

    return units


def combineUnits(*args):
    ret = Counter()
    for l in args:
        ret.update(l)
    return ret


def inverse(units):
    return dict((u, -c) for u, c in units.iteritems())

_debug = 7

definedUnits = []
derivedUnits = []


def unit(cls):
    definedUnits.append(cls)
    return cls


def derivedunit(units=None):
    def derivedunit_decorator(cls):
        cls._complex_base_units = units or cls.__bases__
        derivedUnits.append(cls)
        return cls
    return derivedunit_decorator


def symbol(name):
    def symbol_decorator(cls):
        cls._prettyName = name
        return cls
    return symbol_decorator


@total_ordering
class Unit(object):

    @classmethod
    def prettyName(cls):
        try:
            return cls._prettyName
        except:
            return cls.__name__

    def __init__(self, value, units=None):
        # print 'Creating class %s with units=%s' % (type(self).__name__,
        # units)
        self._value = value
        self._units = Counter()
        try:
            self._units = Counter(units or [type(self)])
        except:
            self._units = Counter([units or type(self)])

    @property
    def Value(self):
        """Get the magnitude of the Unit value."""
        return self._value

    @property
    def Units(self):
        """Get the list of units this object is representing."""
        return Counter(self._units)

    def __repr__(self):
        simple_units = simplify(self.Units)
        names = [(u.__name__, c) for u,c in sorted(simple_units.iteritems(), key=lambda (u, c): -c) ]
        unit_names = dict(names)
        return 'units.Unit({0}, {1!r})'.format(self.Value, unit_names)
        # return self.__str__()

    def __str__(self):
        # print '__str__', self.Units
        simple_units = simplify(self.Units)
        # print [u.prettyName() for u, c in simple_units.iteritems()]
        names = [u.prettyName() if c == 1 else u.prettyName() + '^' + str(c)
                 for u, c in sorted(simple_units.iteritems(), key=lambda (u, c): -c)]
        units_label = ' * '.join(names)
        return '%s%s%s' % (self.Value, ' ' if len(units_label) != 0 else '', units_label)

    def unitEquality(self, other):
        try:
            if self.Units.iteritems() == other.Units.iteritems():
                return True

            if sorted(self.Units.iteritems()) == sorted(other.Units.iteritems()):
                return True

            s = simplify(self.Units)
            o = simplify(other.Units)
            return sorted(s.iteritems()) == sorted(o.iteritems())
            # return sorted(simplify(self.Units)) ==
            # sorted(simplify(other.Units).elements())
        except:
            # other is not a Unit type: check if self has no units
            return simplify(self.Units).iteritems() == []

    def __eq__(self, other):
        # Check for equality of units first, if they are unequal then the
        # arguments are unequal.
        if not self.unitEquality(other):
            return False

        try:
            return self.Value == other.Value

        except:
            return self.Value == other

    def __lt__(self, other):
        if not self.unitEquality(other):
            raise NotImplemented()

        try:
            return self.Value < other.Value
        except:
            return self.Value < other

    def __add__(self, other):
        #        if _debug >= 7:
        #            print 'add : self=%s other=%s' % (self, other)

        # Handle additive identity
        if other == 0:
            return self

        if not self.unitEquality(other):
            raise TypeError(
                'Unable to add "%s" and "%s". Units do not match.' % (self, other))

        try:
            return Unit(self.Value + other.Value, self.Units)

        except:
            return Unit(new_value, self.Units)

    def __radd__(self, other):
        #        if _debug >= 7:
        #            print 'radd: self=%s other=%s' % (self, other)

        # Handle additive identity
        if other == 0:
            return self

        if not self.unitEquality(other):
            raise TypeError(
                'Unable to add "%s" and "%s". Units do not match.' % (self, other))

        try:
            return Unit(self.Value + other.Value, self.Units)

        except:
            return Unit(self.Value + other, self.Units)

    def __sub__(self, other):
        #        if _debug >= 7:
        #            print 'sub : self=%s other=%s' % (self, other)

        # Handle additive identity
        if other == 0:
            return self

        if not self.unitEquality(other):
            raise TypeError(
                'Unable to subtract "%s" and "%s". Units do not match.' % (self, other))

        try:
            return Unit(self.Value - other.Value, self.Units)

        except:
            return Unit(self.Value - other, self.Units)

    def __rsub__(self, other):
        #        if _debug >= 7:
        #            print 'sub : self=%s other=%s' % (self, other)

        # Handle additive identity
        if other == 0:
            return self

        if not self.unitEquality(other):
            raise TypeError(
                'Unable to subtract "%s" and "%s". Units do not match.' % (self, other))

        try:
            return Unit(other.Value - self.Value, self.Units)

        except:
            return Unit(other - self.Value, self.Units)

    def __mul__(self, other):
        # if _debug >= 7:
        #     print 'mul : self=%s other=%s' % (self, other)
        try:
            return Unit(self.Value * other.Value, simplify(combineUnits(self.Units, other.Units)))

        except:
            return Unit(self.Value * other, self.Units)

    def __rmul__(self, other):
        # if _debug >= 7:
        #     print 'rmul: self=%s other=%s' % (self, other)
        return Unit(other * self.Value, self.Units)

    def __div__(self, other):
        # if _debug >= 7:
        #     print 'div : self=%s other=%s' % (self, other)
        try:
            return Unit(self.Value.__div__(other.Value), simplify(combineUnits(self.Units, inverse(other.Units))))

        except:
            return Unit(self.Value / other, self.Units)

    def __truediv__(self, other):
        # if _debug >= 7:
        #     print 'div : self=%s other=%s' % (self, other)
        try:
            return Unit(self.Value.__truediv__(other.Value), simplify(combineUnits(self.Units, inverse(other.Units))))

        except:
            return Unit(self.Value / other, self.Units)

    def __rdiv__(self, other):
        #        if _debug >= 7:
        #            print 'rdiv: self=%s other=%s' % (self, other)
        return Unit(other / self.Value, simplify(inverse(self.Units)))

    def __rtruediv__(self, other):
        #        if _debug >= 7:
        #            print 'rdiv: self=%s other=%s' % (self, other)
        return Unit(other / self.Value, simplify(inverse(self.Units)))

    @classmethod
    def complex_base_units(cls):
        try:
            return cls._complex_base_units
        except:
            return cls.__bases__

    @classmethod
    def base_units(cls):
        # print 'base_units : cls=%s' % (cls,)
        try:
            base_classes = Counter(cls.complex_base_units())
        except:
            base_classes = Counter(cls.__bases__)

        if Unit == cls:
            return Counter()
        elif Unit in base_classes:
            return {cls: 1}
        else:
            base_units = Counter()
            for u, c in base_classes.iteritems():
                base_units.update(
                    dict([(uu, c * cc) for uu, cc in u.base_units().iteritems()]))
            return base_units


@unit
@symbol('m')
class meter(Unit):
    pass


@unit
@symbol('kg')
class kilogram(Unit):
    pass


@unit
@symbol('s')
class second(Unit):
    pass


@unit
@symbol('A')
class ampere(Unit):
    pass


@unit
@symbol('K')
class kelvin(Unit):
    pass


@unit
@symbol('mol')
class mole(Unit):
    pass


@unit
@symbol('Ca')
class candela(Unit):
    pass


@unit
@derivedunit({second: -1})
@symbol('hz')
class hertz(Unit):
    pass


@unit
@derivedunit()
@symbol('C')
class coulomb(ampere, second):
    pass


@unit
@derivedunit({kilogram: 1, meter: 1, second: -2})
@symbol('N')
class newton(Unit):
    pass


@unit
@derivedunit()
@symbol('J')
class joule(newton, meter):
    pass


@unit
@derivedunit()
@symbol('W')
class watt(joule, hertz):
    pass


@unit
@derivedunit({watt: 1, ampere: -1})
@symbol('V')
class volt(Unit):
    pass


@unit
@derivedunit({coulomb: 1, volt: -1})
@symbol('F')
class farad(Unit):
    pass


@unit
@derivedunit({volt: 1, ampere: -1})
@symbol('Ω')
class ohm(Unit):
    pass


@unit
@derivedunit({ampere: 1, volt: -1})
@symbol('S')
class siemens(Unit):
    pass


@unit
@derivedunit({volt: 1, second: -1})
@symbol('Wb')
class weber(Unit):
    pass


@unit
@derivedunit({weber: 1, meter: -2})
@symbol('T')
class tesla(Unit):
    pass


@unit
@derivedunit({weber: 1, ampere: -1})
@symbol('H')
class henry(Unit):
    pass


@unit
@symbol('rad')
class radian(Unit):
    pass


@unit
#@derivedunit({meter: 2, meter: -2})
@symbol('sr')
class steradian(Unit):
    pass


@unit
@derivedunit()
@symbol('lm')
class lumen(candela, steradian):
    pass


@unit
@derivedunit({lumen: 1, meter: -2})
@symbol('lx')
class lux(Unit):
    pass


@unit
@derivedunit({second: -1})
@symbol('Bq')
class steradian(Unit):
    pass


@unit
@derivedunit({joule: 1, kilogram: -1})
@symbol('Gy')
class gray(Unit):
    pass


@unit
@derivedunit({joule: 1, kilogram: -1})
@symbol('Sv')
class sievert(Unit):
    pass


@unit
@derivedunit({mole: 1, second: -1})
@symbol('kat')
class katal(Unit):
    pass


import unittest


class Tester(unittest.TestCase):

    def test_creation_01(self):
        self.assertEqual(joule(2), Unit(1 + 1, joule))
        self.assertFalse(Unit(2, joule) == Unit(2, watt))

    def test_addition_01(self):
        self.assertEqual(joule(2), joule(2) + 0)
        self.assertEqual(joule(2), 0 + joule(2))
        self.assertEqual(joule(4), joule(1) + joule(3))
        try:
            with self.assertRaises(TypeError):
                v = joule(1) + watt(1)
        except TypeError:
            self.assertRaises(TypeError, lambda: joule(1) - watt(1))

    def test_subtraction_01(self):
        self.assertEqual(joule(2), joule(2) - 0)
        self.assertEqual(joule(-2), joule(1) - joule(3))
        try:
            with self.assertRaises(TypeError):
                v = joule(1) - watt(1)
        except TypeError:
            self.assertRaises(TypeError, lambda: joule(1) - watt(1))

    def test_multiplication_01(self):
        self.assertEqual(joule(0), joule(2) * 0)
        self.assertEqual(joule(2), joule(2) * 1)
        self.assertEqual(joule(4), joule(2) * 2)
        self.assertEqual(joule(0), 0 * joule(2))
        self.assertEqual(joule(2), 1 * joule(2))
        self.assertEqual(joule(4), 2 * joule(2))
        self.assertEqual(joule(2), watt(2) * second(1))

    def test_composite_01(self):
        self.assertEqual(joule(4), joule(2) * (second(2) / second(1)))
        self.assertEqual(joule(4), joule(2) * second(2) / second(1))

    def test_division_01(self):
        self.assertEqual(joule(1), joule(2) / 2)
        self.assertEqual(joule(2) / second(1), watt(2))
        self.assertEqual(second(0.001), 1 / hertz(1000.))

    def test_simplify(self):
        self.assertEqual(simplify([watt]), Counter([watt]))
        self.assertEqual(simplify([second, hertz]), Counter([]))
        self.assertEqual(simplify([watt, second]), Counter([joule]))
        self.assertEqual(simplify([joule, hertz]), Counter([watt]))

    def test_strings(self):
        self.assertEqual(str(joule(2)), '2 J')
        self.assertEqual(str(joule(2) * joule(2)), '4 J^2')
        self.assertEqual(str(hertz(2)), '2 hz')
        self.assertEqual(str(1 / hertz(1)), '1 s')


class BasicUnitsTester(unittest.TestCase):

    def test_simplify(self):
        self.assertEqual(simplify([watt]), Counter([watt]))
        self.assertEqual(
            simplify({joule: 1, second: 1}), Counter([joule, second]))
        self.assertEqual(simplify([watt, second]), Counter([joule]))
        self.assertEqual(simplify({joule: 1, second: -1}), Counter([watt]))

        self.assertEqual(simplify([joule, second]), Counter([joule, second]))
        self.assertEqual(simplify([watt]), Counter([watt]))
        self.assertEqual(simplify([watt, second]), Counter([joule]))
        self.assertEqual(simplify([joule, joule]), Counter([joule, joule]))
        self.assertEqual(simplify({joule: 1, second: -1}), Counter([watt]))
        self.assertEqual(
            simplify({kilogram: 1, meter: 1, second: -2}), Counter([newton]))
        self.assertEqual(simplify([hertz]), Counter([hertz]))
        self.assertEqual(simplify({second: -1}), Counter([hertz]))

    def test_base_units(self):
        self.assertEqual(kilogram.base_units(), Counter([kilogram]))
        self.assertEqual(coulomb.base_units(), Counter([ampere, second]))
        self.assertEqual(
            newton.base_units(), {kilogram: 1, meter: 1, second: -2})
        self.assertEqual(
            joule.base_units(), {kilogram: 1, meter: 2, second: -2})
        self.assertEqual(
            watt.base_units(), {kilogram: 1, meter: 2, second: -3})
        self.assertEqual(
            volt.base_units(), {kilogram: 1, meter: 2, second: -3, ampere: -1})

    def test_joule_base_units(self):
        self.assertEqual(
            joule.base_units(), {kilogram: 1, meter: 2, second: -2})


class DerivedUnitTester(unittest.TestCase):

    def test_complex_base_units(self):
        for u in derivedUnits:
            u.complex_base_units()

if __name__ == '__main__':
    # unittest.main()
    # print simplify( joule(2) * (second(2) / second(1)))

    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(Tester))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(DerivedUnitTester))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(BasicUnitsTester))
    suite.addTest(Tester('test_strings'))
    # suite.addTest(BasicUnitsTester('test_joule_base_units'))
    unittest.TextTestRunner(verbosity=2).run(suite)

    # print watt(1) * second(1)
    # print validSimplification( {second:1}, hertz )
    # print simplify([joule, second])
    # print simplify([watt])
    # print simplify([watt, second])
    # print simplify([joule, joule])
    # print simplify({joule:1, second:-1})
    # print simplify({kilogram:1, meter:1, second:-2})
    # print simplify( [hertz] )
