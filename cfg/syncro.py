from cls import *
from cfg.threads import all_cobeginblocks


def joint_synchro(subgraph):
    for cobeginblock in all_cobeginblocks(subgraph):
        _joint_synchro(cobeginblock.threads)


def _joint_synchro(threads):
    events = {event for thread in threads for event in (thread.setevents | thread.waitevents)}
    for event in events:
        setthread = _sole_set(threads, event)
        waitthread = _sole_wait(threads, event)
        if setthread == waitthread or setthread is None or waitthread is None or reach_none(setthread.s, event):
            continue
        setblocks = set()
        waitblocks = set()
        _first_setblocks(setthread.s, event, setblocks)
        _first_waitblocks(waitthread.s, event, waitblocks)

        for setblock in setblocks:
            for waitblock in waitblocks:
                setblock.synchro_exits.add(waitblock)
                waitblock.synchro_entries.add(setblock)


def _sole_set(threads, event):
    buf = None
    for thread in threads:
        if event in thread.setevents:
            if buf is not None:
                return None
            buf = thread
    if event in buf.illegal:
        return None
    return buf


def _sole_wait(threads, event):
    buf = None
    for thread in threads:
        if event in thread.waitevents:
            if buf is not None:
                return None
            buf = thread
    if event in buf.illegal:
        return None
    return buf


def _first_setblocks(block, event, setblocks: set):
    if type(block) == InstBlock:
        inst = block.insts[-1]
        if type(inst) == Set and inst.event == event:
            setblocks.add(block)
            return
    _first_setblocks(block.texit, event, setblocks)
    if type(block) == IfBlock:
        _first_setblocks(block.fexit, event, setblocks)


def _first_waitblocks(block, event, waitblocks: set):
    if block is None:
        return
    if type(block) == InstBlock:
        inst = block.insts[0]
        if type(inst) == Wait and inst.event == event:
            waitblocks.add(block)
            return
    _first_waitblocks(block.texit, event, waitblocks)
    if type(block) == IfBlock:
        _first_waitblocks(block.fexit, event, waitblocks)


def reach_none(block, event):
    if block is None:
        return True
    if type(block) == InstBlock:
        inst = block.insts[-1]
        if type(inst) == Set and inst.event == event:
            return False

    if reach_none(block.texit, event):
        return True
    if type(block) == IfBlock and reach_none(block.fexit, event):
        return True
