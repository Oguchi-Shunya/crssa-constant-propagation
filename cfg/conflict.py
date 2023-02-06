from cls import *
from cfg.threads import all_cobeginblocks


def joint_conflict(subgraph):
    for cobeginblock in all_cobeginblocks(subgraph):
        _joint_conflict(cobeginblock)


def _joint_conflict(cobeginblock):
    threads = cobeginblock.threads
    shares = cobeginblock.shares
    coendblock = cobeginblock.coendblock

    for share in shares:
        list_defblocks = []
        list_refblocks = []

        for thread in threads:
            list_defblocks.append(all_defblocks(thread, share))
            list_refblocks.append(all_refblocks(thread, share))

        for defblock in {defblock for defblocks in list_defblocks for defblock in defblocks}:
            if not killed_synchro(cobeginblock, defblock, share, coendblock):
                _joint_blocks_conflict(cobeginblock, defblock, share)
            if not killed_synchro(defblock, coendblock, share, coendblock):
                _joint_blocks_conflict(defblock, coendblock, share)

        for refblock in {refblock for refblocks in list_refblocks for refblock in refblocks}:
            if not killed_synchro(cobeginblock, refblock, share, coendblock):
                _joint_ref(cobeginblock, refblock, share)

        n = len(threads)
        for i in range(n):
            for j in range(n):
                for pred in list_defblocks[i]:
                    for succ in list_defblocks[j]:
                        if _is_conflict(pred, succ, share, i == j, coendblock):
                            _joint_blocks_conflict(pred, succ, share)
                    for succ in list_refblocks[j]:
                        if _is_conflict(pred, succ, share, i == j, coendblock):
                            _joint_ref(pred, succ, share)


def _joint_blocks_conflict(pred, succ, share):
    pred.conflict_exits[share].add(succ)
    succ.conflict_entries[share].add(pred)


def _joint_ref(pred, succ, share):
    if share not in succ.ref_entries:
        succ.ref_entries[share] = set()
    succ.ref_entries[share].add(pred)


def all_defblocks(thread, share):
    defblocks = set()
    _all_defblocks(thread.s, share, defblocks, Runner(stoptype=EndBlock))
    return defblocks


def _all_defblocks(block, share, defblocks: set, runner: Runner):
    if share in block.piexit:
        defblocks.add(block)
    for succ in runner.exits(block):
        _all_defblocks(succ, share, defblocks, runner)


def all_refblocks(thread, share):
    refblocks = set()
    _all_refblocks(thread.s, share, refblocks, Runner(stoptype=EndBlock))
    return refblocks


def _all_refblocks(block, share, refblocks: set, runner: Runner):
    if block.useonly(share):
        refblocks.add(block)
    for succ in runner.exits(block):
        _all_refblocks(succ, share, refblocks, runner)


def _is_conflict(pred, succ, share, same, stop):
    if same:
        return _is_conflict_same(pred, succ, share, stop)
    return _is_conflict_different(pred, succ, share, stop)


def _is_conflict_different(pred, succ, share, stop):
    if reach_with_synchro(succ, pred):
        # print(1)
        return False
    if killed_synchro(pred, succ, share, stop):
        # print(2)
        return False
    return True


def _is_conflict_same(pred, succ, share, stop):
    if not reach_with_synchro(pred, succ):
        # print(3)
        return False
    if killed_synchro(pred, succ, share, stop):
        # print(4)
        return False
    return True


def reach_with_synchro(start, end):
    return _reach_with_synchro(start, end, Runner(stoptype=CoendBlock))


def _reach_with_synchro(block, end, runner):
    if end in block.with_synchro():
        return True
    for succ in runner.with_synchro(block):
        if _reach_with_synchro(succ, end, runner):
            return True
    return False


def killed_synchro(defblock, useblock, share, stop):
    if type(defblock) == CobeginBlock:
        for succ in defblock.exits():
            if _killed_synchro(succ, useblock, share, stop):
                return True
        return False

    if type(defblock) == IfBlock and not _killed_synchro(defblock.fexit, useblock, share, stop):
        return False
    return _killed_synchro(defblock.texit, useblock, share, stop)


def _killed_synchro(block, useblock, share, stop):
    if block == useblock:
        return False
    if block == stop:
        return False
    if type(block) == InstBlock:
        if share in block.insts[-1].defvars():
            return reach_with_synchro(block, useblock)
    killed = False
    if len(block.synchro_exits) != 0:
        killed = True
        for succ in block.synchro_exits:
            if not _killed_synchro(succ, useblock, share, stop):
                killed = False
                break
    if killed:
        return True
    if type(block) == UntilBlock:
        if search_node(block.fexit, block.fromblock, useblock):
            return _killed_synchro(block.fexit, useblock, share, block.fromblock)
        else:
            return _killed_synchro(block.texit, useblock, share, stop)
    if type(block) == IfBlock and not _killed_synchro(block.fexit, useblock, share, stop):
        return False
    return _killed_synchro(block.texit, useblock, share, stop)


def search_node(block, t, subject):
    if block == subject:
        return True
    if block == t:
        return False
    for succ in block.exits():
        if search_node(succ, t, subject):
            return True
    return False
