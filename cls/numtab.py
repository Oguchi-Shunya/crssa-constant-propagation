from cls.expr import *


class Numtab:
    def __init__(self):
        self.tab = {}

    def copy(self):
        numtab = Numtab()
        numtab.tab = dict(self.tab)
        return numtab

    def attached(self, name):
        if name not in self.tab:
            return name
        return self.tab[name]

    def init(self, name):
        assert name not in self.tab
        self.tab[name] = Numvar(name, 0)

    def attached_inc(self, name):
        numvar = self.tab[name]
        self.tab[name] = Numvar(name, numvar.num + 1)
        return numvar

    def update(self, numvar: Numvar):
        self.tab[numvar.name] = numvar

    def update2(self, name, value):
        self.tab[name] = value

    def names(self):
        return set(self.tab.keys())