from cls import *
from cfg.threads import all_cobeginblocks


def phi2pi(subgraph):
    for cobeginblock in all_cobeginblocks(subgraph):
        coendblock = cobeginblock.coendblock
        shares = cobeginblock.shares

        cobeginblock.piexit |= shares
        coendblock.pientry |= shares
        for share in shares:
            cobeginblock.conflict_exits[share] = set()
            coendblock.conflict_entries[share] = set()

        for thread in cobeginblock.threads:
            _phi2pi(thread.s, shares, Runner(stoptype=EndBlock))


def _phi2pi(block, shares, runner: Runner):
    block.phientry -= shares
    block.phiexit -= shares

    if type(block) == InstBlock:
        defvars = block.insts[-1].defvars() & shares
        block.pientry |= defvars
        block.piexit |= defvars
        for defvar in defvars:
            block.conflict_entries[defvar] = set()
            block.conflict_exits[defvar] = set()

    for succ in runner.exits(block):
        _phi2pi(succ, shares, runner)
