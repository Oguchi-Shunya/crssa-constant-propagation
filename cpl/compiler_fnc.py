from cls import *


def joint_blocks(pred, succ, b_pre, b_post):
    if b_pre:
        pred.texit = succ
    else:
        pred.fexit = succ

    if b_post:
        succ.tentry = pred
    else:
        succ.fentry = pred

    phi = pred.phiexit | succ.phientry
    pred.phiexit = phi
    succ.phientry = phi


def sole_inst(inst):
    instblock = InstBlock([inst])
    subgraph = Subgraph(instblock, instblock)
    subgraph.defvars |= inst.defvars()
    subgraph.usevars |= inst.usevars()
    if type(inst) == Set:
        subgraph.setevents.add(inst.event)
    if type(inst) == Wait:
        subgraph.waitevents.add(inst.event)
    return subgraph


def series(pred_subgraph, succ_subgraph):
    joint_blocks(pred_subgraph.t, succ_subgraph.s, True, True)
    subgraph = Subgraph(pred_subgraph.s, succ_subgraph.t)
    subgraph.absorb(pred_subgraph)
    subgraph.absorb(succ_subgraph)
    return subgraph


def combine(pred_subgraph, succ_subgraph):
    assert succ_subgraph.s == succ_subgraph.t
    assert type(pred_subgraph.t) == type(succ_subgraph.s) == InstBlock
    assert len(succ_subgraph.s.insts) == 1 and succ_subgraph.s.texit is None

    t = pred_subgraph.t
    t.insts.append(succ_subgraph.s.insts[0])
    subgraph = Subgraph(pred_subgraph.s, t)
    subgraph.absorb(pred_subgraph)
    subgraph.absorb(succ_subgraph)
    return subgraph


def sandwiched(content: Subgraph):
    beginblock = BeginBlock()
    endblock = EndBlock()

    joint_blocks(beginblock, content.s, True, True)
    joint_blocks(content.t, endblock, True, True)

    subgraph = Subgraph(beginblock, endblock)
    subgraph.absorb(content)
    return subgraph


def sandwiched_if(ifblock, fiblock, thensubgraph, elsesubgraph):
    subgraph = Subgraph(ifblock, fiblock)
    subgraph.absorb(thensubgraph)
    subgraph.absorb(elsesubgraph)

    ifblock.phiexit |= subgraph.defvars
    fiblock.phientry |= subgraph.defvars

    joint_blocks(ifblock, thensubgraph.s, True, True)
    joint_blocks(ifblock, elsesubgraph.s, False, True)
    joint_blocks(thensubgraph.t, fiblock, True, True)
    joint_blocks(elsesubgraph.t, fiblock, True, False)

    return subgraph


def sandwiched_loop(fromblock, untilblock, dosubgraph, loopsubgraph):
    fromblock.untilblock = untilblock
    untilblock.fromblock = fromblock

    subgraph = Subgraph(fromblock, untilblock)
    subgraph.absorb(dosubgraph)
    subgraph.absorb(loopsubgraph)
    subgraph.illegal |= (subgraph.setevents | subgraph.waitevents)

    fromblock.phientry |= subgraph.defvars
    untilblock.phiexit |= subgraph.defvars

    joint_blocks(fromblock, dosubgraph.s, True, True)
    joint_blocks(dosubgraph.t, untilblock, True, True)
    joint_blocks(untilblock, loopsubgraph.s, False, True)
    joint_blocks(loopsubgraph.t, fromblock, True, False)

    return subgraph


def sandwiched_co(threads: list):
    shares = all_shares(threads)
    cobeginblock = CobeginBlock(threads, shares)
    coendblock = CoendBlock(threads, shares)
    cobeginblock.coendblock = coendblock
    coendblock.cobeginblock = cobeginblock
    subgraph = Subgraph(cobeginblock, coendblock)

    for thread in threads:
        subgraph.defvars |= thread.defvars
        subgraph.usevars |= thread.usevars

    for thread in threads:
        thread.s.tentry = cobeginblock
        thread.t.texit = coendblock

    return subgraph


def all_shares(threads: list):
    shares = set()

    length = len(threads)
    for i in range(length):
        for j in range(length):
            if i == j:
                continue
            shares |= (threads[i].defvars & (threads[j].defvars | threads[j].usevars))

    return shares
