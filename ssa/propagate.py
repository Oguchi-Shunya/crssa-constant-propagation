from cls import *


def propagate_forward(subgraph):
    propagator = Propagator()
    while True:
        propagator.updated = False
        _propagate_forward(subgraph.s, propagator, Runner())
        if not propagator.updated:
            break
    return propagator


def _propagate_forward(block, propagator: Propagator, runner: Runner):
    block.forward(propagator)
    for succ in runner.exits(block):
        _propagate_forward(succ, propagator, runner)


def propagate_backward(subgraph):
    propagator = Propagator()
    while True:
        propagator.updated = False
        _propagate_backward(subgraph.t, propagator, Runner())
        if not propagator.updated:
            break
    return propagator


def _propagate_backward(block, propagator: Propagator, runner: Runner):
    block.backward(propagator)
    for pred in runner.entries(block):
        _propagate_backward(pred, propagator, runner)
