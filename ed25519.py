from util import bytesToNum, numToBytes
from curve import Point, invert, mod
from sha512 import sha512
from typing import List, Tuple


P: int = 2 ** 255 - 19
N: int = 2 ** 252 + 27742317777372353535851937790883648493
D: int = 37095705934669439343138083508754565189542113879843219016388785533085940283555

# Starting Point 'G'.
G: Point = Point(
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960
)


# Convert Point to compressed byte array
def pointToArr(PK: Point, isCompressed: bool) -> List[int]:
    if isCompressed:
        header: int = 3 if PK.y & 1 else 2
        return [header] + numToBytes(PK.x)
    else:
        return [4] + numToBytes(PK.x, 32) + numToBytes(PK.y, 32)


def add(P1: Point, Q1: Point) -> Point:
    x1, y1 = P1.x, P1.y
    x2, y2 = Q1.x, Q1.y

    X1Y2: int = mod(x1 * y2, P)
    X2Y1: int = mod(x2 * y1, P)
    Y1Y2: int = mod(y1 * y2, P)
    X1X2: int = mod(x1 * x2, P)

    XT3: int = mod(X1Y2 + X2Y1, P)
    YT3: int = mod(Y1Y2 - X1X2, P)

    D1: int = mod(X1X2 * Y1Y2, P)
    D2: int = mod(D * D1, P)
    DX: int = mod(1 + D2, P)
    DY: int = mod(1 - D2, P)
    
    x3: int = mod(XT3 * invert(DX, P), P)
    y3: int = mod(YT3 * invert(DY, P), P)

    return Point(x3, y3)


if __name__ == '__main__':
    seed: List[int] = [
        17, 30, 0, 32, 247, 20, 162, 6,
        47, 0, 31, 160, 16, 252, 180, 179,
        136, 24, 172, 113, 103, 72, 59, 104,
        135, 229, 132, 209, 107, 129, 161, 171
    ]

    sk: List[int] = sha512(seed)
    head: List[int] = sk[:32]
    head[0] &= 248
    head[31] &= 127
    head[31] |= 64
    privKey: int = bytesToNum(head) % N

    C: Point = Point(32, 64)
    print(add(G, C))