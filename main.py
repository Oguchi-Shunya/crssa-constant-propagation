import sys
import cfg
import cpl
import ssa
from output import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit()
    subgraph = cpl.code2ctrl(sys.argv[1])
    print("----- CRCFG -----------------------------------------------------")
    cfg.ctrl2crcfg(subgraph)
    print_subgraph(subgraph, print_crcfg_block)
    print("----- CRSSA -----------------------------------------------------")
    ssa.crcfg2crssa(subgraph)
    print_subgraph(subgraph, print_crssa_block)
    print("----- Constant Propagation -----------------------------------------------------")
    forward = ssa.propagate_forward(subgraph)
    backward = ssa.propagate_backward(subgraph)
    print_propagation(forward, backward)
