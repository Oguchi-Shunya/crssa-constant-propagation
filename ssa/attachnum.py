from cls import *


def attach_defnum(subgraph):
    numtab = Numtab()
    _attach_defnum(subgraph.s, numtab, Runner())


def _attach_defnum(block, numtab: Numtab, runner):
    block.attach_defnum(numtab)
    for succ in runner.exits(block):
        _attach_defnum(succ, numtab, runner)


def attach_usenum(subgraph):
    numtab = Numtab()
    _attach_usenum(subgraph.s, numtab, Runner(), {})
    _attach_piref(subgraph.s, Runner())


def _attach_usenum(block, numtab: Numtab, runner, assemble: dict):
    block.attach_usenum(numtab)
    if type(block) == CobeginBlock:
        assemble[block.coendblock] = []
    if type(block.texit) == CoendBlock:
        coendblock = block.texit
        numtabs = assemble[coendblock]
        numtabs.append(numtab)
        if len(numtabs) != len(coendblock.threads):
            return
        merge_numtabs(numtab, numtabs, coendblock.threads, coendblock.shares)

    for succ in runner.exits(block):
        _attach_usenum(succ, numtab.copy(), runner, assemble)


def _attach_piref(block, runner):
    block.attach_piref()
    for succ in runner.exits(block):
        _attach_piref(succ, runner)


def merge_numtabs(numtab, numtabs, threads, shares):
    for nonshare in numtab.names() - shares:
        for i in range(len(threads)):
            if nonshare not in threads[i].defvars:
                continue
            numtab.update2(nonshare, numtabs[i].attached(nonshare))
