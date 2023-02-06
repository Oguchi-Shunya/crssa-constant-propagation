from cls.runner import *


class SubgraphNums:
    def __init__(self):
        self.num = -1
        self.nums = {None: None}

    def setnum(self, block):
        self.num += 1
        self.nums[block] = self.num


def _cntstr(s):
    if len(s) == 0:
        return ""
    return str(s)[1:-1]


def _blocks2str(nums, blocks):
    return str([nums[block] for block in blocks])[1:-1]


def _dict2str(nums, dct: dict):
    return str({key: _blocks2str(nums, dct[key]) for key in dct})[1:-1]


def _col(s, color=31):
    return f"\033[{color}m{s}\033[0m"


def subgraph_nums(subgraph):
    nums = SubgraphNums()
    _subgraph_nums(subgraph.s, Runner(), nums)
    return nums.nums


def _subgraph_nums(block, runner: Runner, nums: SubgraphNums):
    nums.setnum(block)
    for succ in runner.exits(block):
        _subgraph_nums(succ, runner, nums)


def print_subgraph(subgraph, func):
    nums = subgraph_nums(subgraph)
    _print_subgraph(subgraph.s, Runner(), nums, func)


def _print_subgraph(block, runner: Runner, nums: dict, func):
    func(block, nums)
    for succ in runner.exits(block):
        _print_subgraph(succ, runner, nums, func)


def print_crcfg_block(block, nums: dict):
    print(f"{nums[block]}: {block}")
    if len(block.ref_entries) != 0:
        print(_col(f"ref <{_dict2str(nums, block.ref_entries)}>", 33))
    print(f"-> ", end="")
    print(_col(f"[{_blocks2str(nums, block.exits())}]"), end="")
    if len(block.synchro_exits) != 0:
        print(_col(f" ${_blocks2str(nums, block.synchro_exits)}$", 36), end="")
    if len(block.conflict_exits) != 0:
        print(_col(f" <{_dict2str(nums, block.conflict_exits)}>", 34), end="")
    print()
    print()


def print_crssa_block(block, nums: dict):
    print(f"{nums[block]}: {block}")
    if not (len(block.phientry) == len(block.phiexit) == 0):
        print(f"({_cntstr(block.phientry)}) => ({_cntstr(block.phiexit)})")
    if not (len(block.pientry) == len(block.piexit) == 0):
        print(f"<{_cntstr(block.pientry)}> => <{_cntstr(block.piexit)}>")
    print(_col(f"[{_blocks2str(nums, block.exits())}]"), end="")
    if len(block.synchro_exits) != 0:
        print(_col(f" ${_blocks2str(nums, block.synchro_exits)}$", 36), end="")
    if len(block.conflict_exits) != 0:
        print(_col(f" <{_dict2str(nums, block.conflict_exits)}>", 34), end="")
    print()
    print()


def fll(a, maxlen):
    a = str(a)
    return ' ' * (maxlen - len(a)) + a


def print_propagation(forward, backward):
    numvars = []
    for numvar in forward.table:
        numvars.append(numvar)
    numvars.sort()

    maxnamelen = max([len(str(numvar)) for numvar in numvars])
    maxflen = max([len(str(forward.table[numvar])) for numvar in numvars])
    maxblen = max([len(str(backward.table[numvar])) for numvar in numvars])
    maxflen = max(maxflen, 8)
    maxblen = max(maxblen, 8)
    print(f"{fll('', maxnamelen)}  {fll('forward', maxflen)} : {fll('backward', maxblen)}")
    for numvar in numvars:
        fvalue = forward.table[numvar]
        bvalue = backward.table[numvar]
        m = f"{fll(numvar, maxnamelen)}  {fll(fvalue, maxflen)} : {fll(bvalue, maxblen)}"
        if fvalue != bvalue or type(fvalue) != type(bvalue):
            print(_col(m))
        else:
            print(m)
