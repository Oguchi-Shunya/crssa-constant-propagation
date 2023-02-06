from cls.expr import *
from cls.propagator import Propagator


class Inst:
    def __repr__(self):
        return str(self)

    def defvars(self):
        return set()

    def usevars(self):
        return set()

    def attach_defnum(self, numtab):
        pass

    def attach_usenum(self, numtab):
        pass

    def forward(self, propagator: Propagator):
        pass

    def backward(self, propagator: Propagator):
        pass


class Skip(Inst):
    def __init__(self):
        pass

    def __str__(self):
        return "skip"


class Set(Inst):
    def __init__(self, event: str):
        self.event = event

    def __str__(self):
        return f"set {self.event}"


class Wait(Inst):
    def __init__(self, event: str):
        self.event = event

    def __str__(self):
        return f"wait {self.event}"


class Local(Inst):
    def __init__(self, x, expr: Expr):
        self.x = x
        self.expr = expr

    def __str__(self):
        return f"{self.x} := {self.expr}"

    def defvars(self):
        return {self.x}

    def usevars(self):
        return self.expr.usevars()

    def attach_defnum(self, numtab):
        numtab.init(self.x)
        self.x = numtab.attached_inc(self.x)

    def attach_usenum(self, numtab):
        self.expr.attach_usenum(numtab)
        numtab.update(self.x)

    def forward(self, propagator: Propagator):
        propagator.write(self.x, propagator.evl_expr(self.expr))


class Delocal(Inst):
    def __init__(self, x, expr: Expr):
        self.x = x
        self.expr = expr

    def __str__(self):
        return f"{self.expr} := {self.x}"

    def usevars(self):
        return {self.x} | self.expr.usevars()

    def attach_usenum(self, numtab):
        self.expr.attach_usenum(numtab)
        self.x = numtab.attached(self.x)

    def backward(self, propagator: Propagator):
        propagator.write(self.x, propagator.evl_expr(self.expr))


class Update(Inst):
    def __init__(self, x: str, btype: Btype, expr: Expr):
        self.x1 = x
        self.x0 = x
        self.btype = btype
        self.expr = expr

    def __str__(self):
        if type(self.x1) == type(self.x0) == str:
            return f"{self.x1} {self.btype}= {self.expr}"
        return f"{self.x1} := {self.x0} {self.btype} ({self.expr})"

    def defvars(self):
        return {self.x1}

    def usevars(self):
        return {self.x0} | self.expr.usevars()

    def attach_defnum(self, numtab):
        self.x1 = numtab.attached_inc(self.x1)

    def attach_usenum(self, numtab):
        self.x0 = numtab.attached(self.x0)
        self.expr.attach_usenum(numtab)
        numtab.update(self.x1)

    def forward(self, propagator: Propagator):
        value1 = propagator.evl_r(self.x0)
        value2 = propagator.evl_expr(self.expr)
        propagator.write(self.x1, Propagator.calc(value1, value2, self.btype))

    def backward(self, propagator: Propagator):
        value1 = propagator.evl_r(self.x1)
        value2 = propagator.evl_expr(self.expr)
        propagator.write(self.x0, Propagator.calc(value1, value2, self.btype.inv()))


class Exchange(Inst):
    def __init__(self, x: str, y: str):
        self.x1 = x
        self.x0 = x
        self.y1 = y
        self.y0 = y

    def __str__(self):
        if type(self.x1) == type(self.x0) == type(self.y1) == type(self.y0) == str:
            return f"{self.x1} <=> {self.y1}"
        return f"{self.x1}, {self.y1} := {self.y0}, {self.x0}"

    def defvars(self):
        return {self.x1, self.y1}

    def usevars(self):
        return {self.x0, self.y0}

    def attach_defnum(self, numtab):
        self.x1 = numtab.attached_inc(self.x1)
        self.y1 = numtab.attached_inc(self.y1)

    def attach_usenum(self, numtab):
        self.x0 = numtab.attached(self.x0)
        self.y0 = numtab.attached(self.y0)
        numtab.update(self.x1)
        numtab.update(self.y1)

    def forward(self, propagator: Propagator):
        propagator.write(self.x1, propagator.evl_r(self.y0))
        propagator.write(self.y1, propagator.evl_r(self.x0))

    def backward(self, propagator: Propagator):
        propagator.write(self.x0, propagator.evl_r(self.y1))
        propagator.write(self.y0, propagator.evl_r(self.x1))


class Excmem(Inst):
    def __init__(self, x: str, i: str):
        self.x1 = x
        self.x0 = x
        self.i = i

    def __str__(self):
        if type(self.x1) == type(self.x0) == type(self.i) == str:
            return f"{self.x1} <=> M[{self.i}]"
        return f"{self.x1} := M[{self.i}] := {self.x0}"

    def defvars(self):
        return {self.x1}

    def usevars(self):
        return {self.x0, self.i}

    def attach_defnum(self, numtab):
        self.x1 = numtab.attached_inc(self.x1)

    def attach_usenum(self, numtab):
        self.x0 = numtab.attached(self.x0)
        self.i = numtab.attached(self.i)
        numtab.update(self.x1)

    def forward(self, propagator: Propagator):
        propagator.write(self.x1, False)

    def backward(self, propagator: Propagator):
        propagator.write(self.x0, False)
