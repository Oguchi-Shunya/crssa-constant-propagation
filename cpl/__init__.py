from cpl.compiler import compile
from cpl.combine import combine
from cpl.phi2pi import phi2pi


def code2ctrl(path):
    subgraph = compile(path)
    combine(subgraph)
    phi2pi(subgraph)
    return subgraph
