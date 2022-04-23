from util import bytesToNum, numToBytes
from curve import Point, invert, mod
from sha512 import sha512
from typing import List, Tuple


P: int = 2 ** 255 - 19
N: int = 2 ** 252 + 27742317777372353535851937790883648493
D: int = mod(-121665 * invert(121666, P), P)

# Starting Point 'G'.
G: Point = Point(
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960
)


# https://en.wikipedia.org/wiki/Edwards_curve
# https://sefiks.com/2018/12/24/a-gentle-introduction-to-edwards-curve-digital-signature-algorithm-eddsa/
def add(P1: Point, Q1: Point) -> Point:
    x1, y1 = P1.x, P1.y
    x2, y2 = Q1.x, Q1.y

    x3: int = (((x1 * y2 + y1 * x2) % P) * invert(1 + D * x1 * x2 * y1 * y2, P)) % P
    y3: int = (((y1 * y2 + x1 * x2) % P) * invert(1 - D * x1 * x2 * y1 * y2, P)) % P

    return Point(x3, y3)


def bytesToNumberLE(head: List[int]) -> int:
    value: int = 0
    for i in range(len(head)):
        value += head[i] << (8 * i)
    return value


def prepKey(sk: List[int]) -> int:
    head: List[int] = sha512(sk)[:32]
    head[0] &= 248
    head[31] &= 127
    head[31] |= 64
    return bytesToNumberLE(head) % N


if __name__ == '__main__':
    seed: List[int] = [
        17, 30, 0, 32, 247, 20, 162, 6, 47, 0, 31, 160, 16, 252, 180, 179, 136,
        24, 172, 113, 103, 72, 59, 104, 135, 229, 132, 209, 107, 129, 161, 171
    ]
    
    privKey: int = prepKey(seed)
    C: Point = Point(64, 32)
    sum: Point = add(G, C)
    print(sum)
