from util import numToBytes
from typing import List


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def toArray(self, isCompressed: bool = True) -> List[int]:
        if isCompressed:
            header: int = 3 if self.y & 1 else 2
            return [header] + numToBytes(self.x)
        else:
            return [4] + numToBytes(self.x, 32) + numToBytes(self.y, 32)

    def set(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def clear(self) -> None:
        self.x = 0
        self.y = 0

    def __repr__(self) -> str:
        return f'x: {self.x}\ny: {self.y}'


def mod(a: int, modulo: int) -> int:
    if a < 0:
        return a - modulo
    return a % modulo


# Compute the greatest common divisor of ints 'a' and 'modulo'.
def invert(a: int, modulo: int) -> int:
    return pow(a, modulo - 2, modulo)