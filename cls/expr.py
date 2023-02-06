from enum import Enum

int2str = ['+', '-', '^', '==', '!=', '<', '>', '<=', '>=']
str2int = {s: i for i, s in enumerate(int2str)}


class Btype(Enum):
    PLUS = 0
    MINUS = 1
    XOR = 2
    EQ = 3
    NEQ = 4
    LT = 5
    GT = 6
    LE = 7
    GE = 8

    @classmethod
    def str2btype(cls, s):
        return Btype(str2int[s])

    def __str__(self):
        return int2str[self.value]

    def eval(self, i1, i2):
        return int(eval(f"{i1} {self} {i2}"))

    def inv(self):
        match self:
            case Btype.PLUS:
                return Btype.MINUS
            case Btype.MINUS:
                return Btype.PLUS
            case Btype.XOR:
                return Btype.XOR
            case _:
                assert False


class Numvar:
    def __init__(self, name: str, num: int):
        self.name = name
        self.num = num

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.num is None:
            return f"{self.name}_~"
        return f"{self.name}_{self.num}"

    def __eq__(self, other):
        return self.name == other.name and self.num == other.num

    def __hash__(self):
        return hash((self.name, self.num))

    def __lt__(self, other):
        if self.name == other.name:
            if self.num is None:
                return True
            if other.num is None:
                return False
            return self.num < other.num
        return self.name < other.name


class Piref:
    def __init__(self, args):
        self.args = args

    def __str__(self):
        return f"π({str(self.args)[1:-1]})"

    def __repr__(self):
        return str(self)


class Expr:
    def __init__(self, r1, btype, r2):
        self.r1 = r1
        self.btype = btype
        self.r2 = r2

    def usevars(self):
        usevars = set()
        if type(self.r1) == str:
            usevars.add(self.r1)
        if type(self.r2) == str:
            usevars.add(self.r2)
        return usevars

    def usenumvars(self):
        usevars = set()
        if type(self.r1) == Numvar:
            usevars.add(self.r1)
        if type(self.r2) == str:
            usevars.add(self.r2)
        return usevars

    def attach_usenum(self, numtab):
        if type(self.r1) != int:
            self.r1 = numtab.attached(self.r1)
        if type(self.r2) != int:
            self.r2 = numtab.attached(self.r2)

    def __str__(self):
        return f"{self.r1} {self.btype} {self.r2}"

    def __repr__(self):
        return str(self)
