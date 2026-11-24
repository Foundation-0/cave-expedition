import json, re, os
from fractions import Fraction as F
# the package folder (verification/outside/gate5-unification), found relative to this file
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def jload(rel):
    with open(os.path.join(BASE, rel), encoding='utf-8') as fh:
        return json.load(fh)


def fr(s):
    return F(s)


def fmat(rows):
    return [[F(x) for x in r] for r in rows]


def sqrt_exact(n):
    import math
    r = math.isqrt(n)
    return r if r * r == n else None


def is_rational_square(x):
    """x Fraction >= 0: is it a square of a rational?"""
    x = F(x)
    if x < 0:
        return False
    return sqrt_exact(x.numerator) is not None and sqrt_exact(x.denominator) is not None


def same_square_class(a, b):
    """a, b nonzero rationals: a/b is a rational square (signs included)"""
    a, b = F(a), F(b)
    if a == 0 or b == 0:
        return a == b
    return is_rational_square(a * b)


class Rec:
    """collects pass/fail lines; prints at the end"""
    def __init__(self):
        self.lines = []
        self.bad = []

    def p(self, *a):
        s = ' '.join(str(x) for x in a)
        print(s)

    def check(self, name, cond, detail=''):
        print(('OK   ' if cond else 'FAIL ') + name + (' :: ' + str(detail) if detail != '' else ''))
        if not cond:
            self.bad.append(name)
        return cond
