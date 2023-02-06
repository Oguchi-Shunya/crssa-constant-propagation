from ssa.attachnum import attach_usenum, attach_defnum
from ssa.propagate import *


def crcfg2crssa(subgraph):
    attach_defnum(subgraph)
    attach_usenum(subgraph)
