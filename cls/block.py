from cls.numtab import Numtab
from cls.propagator import Propagator
from cls.expr import *


def search_name(varnums, name):
    for varnum in varnums:
        if varnum.name == name:
            return varnum
    assert False

class Block:
    def __init__(self):
        self.tentry = None
        self.texit = None

        self.synchro_entries = set()
        self.synchro_exits = set()
        self.conflict_entries = dict()
        self.conflict_exits = dict()
        self.ref_entries = dict()

        self.phientry = set()
        self.phiexit = set()
        self.pientry = set()
        self.piexit = set()

    def __repr__(self):
        return str(self)

    def entries(self):
        return [self.tentry]

    def exits(self):
        return [self.texit]

    def with_synchro(self):
        return set(self.exits()) | self.synchro_exits

    def useonly(self, share):
        return False

    def attach_defnum(self, numtab):
        self.phientry = {numtab.attached_inc(name) for name in self.phientry}
        self.pientry = {numtab.attached_inc(name) for name in self.pientry}

    def attach_usenum(self, numtab):
        for numvar in self.phientry:
            numtab.update(numvar)
        for numvar in self.pientry:
            numtab.update(numvar)

        for name in self.ref_entries:
            numtab.update2(name, name)

        self._attach_usenum(numtab)

        self.phiexit = {numtab.attached(name) for name in self.phiexit}
        self.piexit = {numtab.attached(name) for name in self.piexit}

    def _attach_usenum(self, numtab):
        pass

    def attach_piref(self):
        numtab = Numtab()
        for name in self.ref_entries:
            args = []
            for defblock in self.ref_entries[name]:
                args.append(search_name(defblock.piexit, name))
            numtab.update2(name, Piref(args))
        self._attach_usenum(numtab)

    def forward(self, propagator: Propagator):
        for name in self.conflict_exits:
            defvar = search_name(self.piexit, name)
            value = propagator.evl_r(defvar)
            for useblock in self.conflict_exits[name]:
                numvar = search_name(useblock.pientry, name)
                propagator.write(numvar, value)

        for defvar in self.phiexit:
            value = propagator.evl_r(defvar)
            for useblock in self.exits():
                numvar = search_name(useblock.phientry, defvar.name)
                propagator.write(numvar, value)

    def backward(self, propagator: Propagator):
        for name in self.conflict_entries:
            defvar = search_name(self.pientry, name)
            value = propagator.evl_r(defvar)
            for useblock in self.conflict_entries[name]:
                numvar = search_name(useblock.piexit, name)
                propagator.write(numvar, value)

        for defvar in self.phientry:
            value = propagator.evl_r(defvar)
            for useblock in self.entries():
                numvar = search_name(useblock.phiexit, defvar.name)
                propagator.write(numvar, value)


##########################################################################################
class CondBlock(Block):
    def __init__(self, cond: Expr):
        super().__init__()
        self.cond = cond

    def useonly(self, share):
        return share in self.cond.usevars()

    def _attach_usenum(self, numtab):
        self.cond.attach_usenum(numtab)


class BranchBlock(CondBlock):
    def __init__(self, cond: Expr):
        super().__init__(cond)
        self.fexit = None

    def exits(self):
        return [self.texit, self.fexit]


class ConfluentBlock(CondBlock):
    def __init__(self, cond: Expr):
        super().__init__(cond)
        self.fentry = None

    def entries(self):
        return [self.tentry, self.fentry]


class CoBlock(Block):
    def __init__(self, threads, shares):
        super().__init__()
        self.threads = threads
        self.shares = shares


##########################################################################################
class IfBlock(BranchBlock):
    def __str__(self):
        return f"if {self.cond}"


class FiBlock(ConfluentBlock):
    def __str__(self):
        return f"fi {self.cond}"


class FromBlock(ConfluentBlock):
    def __str__(self):
        return f"from {self.cond}"


class UntilBlock(BranchBlock):
    def __str__(self):
        return f"until {self.cond}"


class BeginBlock(Block):
    def __str__(self):
        return f"begin"


class EndBlock(Block):
    def __str__(self):
        return f"end"


class CobeginBlock(CoBlock):
    def __init__(self, threads, shares):
        super().__init__(threads, shares)
        self.coendblock = None

    def __str__(self):
        return f"cobegin"

    def exits(self):
        return [thread.s for thread in self.threads]


class CoendBlock(CoBlock):
    def __init__(self, threads, shares):
        super().__init__(threads, shares)
        self.cobeginblock = None

    def __str__(self):
        return f"coend"

    def entries(self):
        return [thread.t for thread in self.threads]


##########################################################################################
class InstBlock(Block):
    def __init__(self, insts: list):
        super().__init__()
        self.insts = insts

    def __str__(self):
        return f"inst{self.insts}"

    def useonly(self, share):
        inst = self.insts[0]
        return share in (inst.usevars() - inst.defvars())

    def attach_defnum(self, numtab):
        super().attach_defnum(numtab)
        for inst in self.insts:
            inst.attach_defnum(numtab)

    def _attach_usenum(self, numtab):
        for inst in self.insts:
            inst.attach_usenum(numtab)

    def forward(self, propagator: Propagator):
        for inst in self.insts:
            inst.forward(propagator)
        super().forward(propagator)

    def backward(self, propagator: Propagator):
        for inst in reversed(self.insts):
            inst.backward(propagator)
        super().backward(propagator)



