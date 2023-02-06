class Subgraph:
    def __init__(self, s, t):
        self.s = s
        self.t = t

        self.defvars = set()
        self.usevars = set()
        self.setevents = set()
        self.waitevents = set()
        self.illegal = set()

    def absorb(self, others):
        self.defvars |= others.defvars
        self.usevars |= others.usevars
        self.setevents |= others.setevents
        self.waitevents |= others.waitevents
        self.illegal |= others.illegal
