from cfg.syncro import joint_synchro
from cfg.conflict import joint_conflict


def ctrl2crcfg(subgraph):
    joint_synchro(subgraph)
    joint_conflict(subgraph)
