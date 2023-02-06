from cls import *


def combine(subgraph, shares=None):
    if shares is None:
        shares = set()
    _combine(subgraph.s, shares, Runner(stoptype=EndBlock))


def _combine(block, shares: set, runner: Runner):
    while _combine_block(block, shares):
        pass
    if type(block) == CobeginBlock:
        for thread in block.threads:
            combine(thread, block.shares)

        for succ in runner.exits(block.coendblock):
            _combine(succ, shares, runner)
    else:
        for succ in runner.exits(block):
            _combine(succ, shares, runner)


def _combine_block(block: InstBlock, shares: set) -> bool:
    if not (type(block) == type(block.texit) == InstBlock):
        return False
    last_inst = block.insts[-1]
    first_inst = block.texit.insts[0]
    if type(first_inst) == Wait or type(last_inst) == Set:
        return False
    if not shares.isdisjoint(first_inst.usevars()) or not shares.isdisjoint(last_inst.defvars()):
        return False

    original = block.texit
    succ = block.texit.texit
    assert succ is not None

    block.phiexit |= original.phiexit
    block.insts = block.insts + original.insts
    block.texit = succ
    if issubclass(type(succ), ConfluentBlock) and succ.fentry == original:
        succ.fentry = block
    else:
        assert succ.tentry == original
        succ.tentry = block

    return True
