from util import numToBytes, bytesToNum
from curve import Point, invert, mod
from sha512 import sha512, hmac512
from random import randint
from typing import List


A: int = -1
P: int = 2 ** 255 - 19
N: int = 2 ** 252 + 27742317777372353535851937790883648493
D: int = mod(-121665 * invert(121666, P), P)

# Starting Point 'G'.
G: Point = Point(
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960
)


def unsafeAdd(Q: Point, R: Point) -> None:
    x1: int = Q.x
    x2: int = R.x

    Q.x = mod(mod(x1 * R.y + Q.y * x2, P) * invert(1 + D * x1 * x2 * Q.y * R.y, P), P)
    Q.y = mod(mod(Q.y * R.y - A * x1 * x2, P) * invert(1 - D * x1 * x2 * Q.y * R.y, P), P)


def add(Q: Point, R: Point) -> None:
    if Q.x == R.x and Q.y == -R.y: Q.clear()
    elif Q.x == 0 or Q.y == 0: Q.set(R.x, R.y)
    elif R.x != 0 and R.y != 0: unsafeAdd(Q, R)


def multiply(Q: Point, k: int) -> Point:
    G: Point = Point(Q.x, Q.y)
    S: Point = Point(0, 0)
    while k:
        if k & 1: add(S, G)
        add(G, G)           # Double
        k >>= 1
    return S


# Calculate public key from secret key.
def getPublicKey(sk: List[int]) -> List[int]:
    head: List[int] = sha512(sk)[:32]
    head[0] &= 248
    head[31] &= 127
    head[31] |= 64
    secretKey: int = bytesToNum(head, 'le') % N

    # Multiply Point 'G' by int 'secretKey' to find public key.
    pk: Point = multiply(G, secretKey)
    return sk + numToBytes(pk.y, 32, 'le')


if __name__ == '__main__':
    sk: List[int] = [
        17, 30, 0, 32, 247, 20, 162, 6, 47, 0, 31, 160, 16, 252, 180, 179, 136,
        24, 172, 113, 103, 72, 59, 104, 135, 229, 132, 209, 107, 129, 161, 171
    ]
    
    """
    [179, 150, 69, 63, 22, 230, 21, 230, 22, 128, 202, 77, 178, 128, 31, 151,
    100, 99, 195, 143, 2, 192, 223, 239, 118, 151, 17, 72, 152, 242, 42, 117]
    """
    pk: List[int] = getPublicKey(sk)
    print('Public key:', pk)
