from cls.expr import *


class Propagator:
    def __init__(self):
        self.table = {}
        self.updated = False

    def evl_numvar(self, numvar):
        if numvar not in self.table:
            self.table[numvar] = True
        return self.table[numvar]

    def evl_piref(self, piref):
        values = {self.evl_numvar(arg) for arg in piref.args}
        for value in values:
            if value is True:
                return True
        for value in values:
            if value is False:
                return False
        if len(values) >= 2:
            return False
        return self.evl_numvar(piref.args[0])

    def evl_r(self, r):
        typ = type(r)
        if typ == int: return r
        if typ == Numvar: return self.evl_numvar(r)
        if typ == Piref: return self.evl_piref(r)
        assert False

    def evl_expr(self, expr):
        return Propagator.calc(self.evl_r(expr.r1), self.evl_r(expr.r2), expr.btype)

    @classmethod
    def calc(cls, value1, value2, btype):
        if value1 is True or value2 is True:
            return True
        if value1 is False or value2 is False:
            return False
        match btype:
            case Btype.PLUS:
                return value1 + value2
            case Btype.MINUS:
                return value1 - value2
            case _:
                assert False

    def write(self, numvar, value):
        pre = self.evl_numvar(numvar)
        if pre is True:
            self.table[numvar] = value
        elif value is True:
            self.table[numvar] = pre
        elif pre is False or value is False:
            self.table[numvar] = False
        elif pre != value:
            self.table[numvar] = False
        elif pre == value:
            self.table[numvar] = pre
        else:
            assert False

        if pre != self.evl_numvar(numvar):
            self.updated = True
