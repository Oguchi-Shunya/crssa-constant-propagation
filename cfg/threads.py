from cls import *


def all_cobeginblocks(subgraph):
    cobeginblocks = set()
    _all_cobeginblocks(subgraph.s, cobeginblocks, Runner())
    return cobeginblocks


def _all_cobeginblocks(block, cobeginblocks, runner: Runner):
    if type(block) == CobeginBlock:
        cobeginblocks.add(block)
        for succ in runner.exits(block.coendblock):
            _all_cobeginblocks(succ, cobeginblocks, runner)
    else:
        for succ in runner.exits(block):
            _all_cobeginblocks(succ, cobeginblocks, runner)
