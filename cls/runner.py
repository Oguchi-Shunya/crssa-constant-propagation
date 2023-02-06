class Runner:
    def __init__(self, stoptype=type(None)):
        self.checked = set()
        self.stoptype = stoptype

    def exits(self, block):
        self.checked.add(block)
        exits = []
        for succ in block.exits():
            if succ not in self.checked and type(succ) != self.stoptype:
                self.checked.add(succ)
                exits.append(succ)
        return exits

    def entries(self, block):
        self.checked.add(block)
        entries = []
        for succ in block.entries():
            if succ not in self.checked and type(succ) != self.stoptype:
                self.checked.add(succ)
                entries.append(succ)
        return entries

    def synchro_exits(self, block):
        self.checked.add(block)
        exits = []
        for succ in block.synchro_exits:
            if succ not in self.checked and type(succ) != self.stoptype:
                self.checked.add(succ)
                exits.append(succ)
        return exits

    def with_synchro(self, block):
        self.checked.add(block)
        exits = []
        for succ in block.with_synchro():
            if succ not in self.checked and type(succ) != self.stoptype:
                self.checked.add(succ)
                exits.append(succ)
        return exits
