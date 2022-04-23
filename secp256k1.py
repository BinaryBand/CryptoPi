from util import bytesToNum, numToBytes
from curve import Point, invert, mod
from sha256 import hmac256
from random import randint
from typing import List


P: int = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
N: int = 2 ** 256 - 432420386565659656852420866394968145599

# Starting Point 'G' for 'secp256k1'.
# 02 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798
G: Point = Point(
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424
)


def ArrToPoint(key: List[int]) -> Point:
    # If 'key' is compressed, calculate 'y' from 'x'.
    if len(key) == 32 or (key[0] == 2 or key[0] == 3):
        assert 32 <= len(key) <= 33, 'Compressed key must be of length 32 or 33.'
        x: int = bytesToNum(key[-32:])
        y: int = pow(x ** 3 + 7, (P + 1) // 4, P)   # y = y² ^ (p + 1) / 4
        return Point(x, y)

    # If 'key' is not compressed.
    elif len(key) == 64 or (key[0] == 4):
        assert 64 <= len(key) <= 65, 'Non-compressed key must be of length 64 or 65.'
        x: int = bytesToNum(key[-64:-32])
        y: int = bytesToNum(key[-32:])
        return Point(x, y)


def unsafeAdd(Q: Point, R: Point) -> None:
    x1: int = Q.x

    m: int = mod((R.y - Q.y) * invert(R.x - x1, P), P)
    Q.x = mod(m ** 2 - x1 - R.x, P)
    Q.y = mod(m * (x1 - Q.x) - Q.y, P)


# Add two points together.
def add(Q: Point, R: Point) -> None:
    if Q.x == R.x and Q.y == R.y: double(Q)
    elif Q.x == R.x and Q.y == -R.y: Q.clear()
    elif Q.x == 0 or Q.y == 0: Q.set(R.x, R.y)
    elif R.x != 0 and R.y != 0: unsafeAdd(Q, R)


# Add point to itself.
def double(Q: Point) -> None:
    x1: int = Q.x
    y1: int = Q.y

    m: int = mod(3 * x1 ** 2 * invert(2 * y1, P), P)
    Q.x = mod(m ** 2 - x1 * 2, P)
    Q.y = mod(m * (x1 - Q.x) - y1, P)


def multiply(Q: Point, n: int) -> Point:
    G: Point = Point(Q.x, Q.y)
    S: Point = Point(0, 0)
    while n:
        if n & 1: add(S, G)
        double(G)
        n >>= 1
    return S


# Calculate public key from secret key.
def getPublicKey(sk: List[int], isCompressed: bool = False) -> List[int]:
    secretKey: int = mod(bytesToNum(sk), P)
    PK: Point = multiply(G, secretKey)      # Multiply Point 'G' by int 'secretKey' to find public key.

    # Convert public key from Point to byte array before returning it.
    return PK.toArray(isCompressed)


# Sign message using secret key.
def sign(msg: List[int], sk: List[int], entropy: List[int]) -> List[int]:
    message: int = bytesToNum(msg)
    secretKey: int = bytesToNum(sk)

    r: int = 0
    s: int = 0
    while r == 0 or s == 0:
        entropy: List[int] = hmac256(msg, entropy)
        seed: int = bytesToNum(entropy)
        r = multiply(G, seed).x
        s = ((message + r * secretKey) * invert(seed, N)) % N

    return numToBytes(r, 32) + numToBytes(s, 32)


# Verify signature is valid using public key.
def verify(sig: List[int], msg: List[int], pk: List[int]) -> bool:
    message: int = bytesToNum(msg)
    publicKey: int = ArrToPoint(pk)

    r: int = bytesToNum(sig[:32])
    s: int = bytesToNum(sig[32:])

    # Probably forged, protect against fault attacks.
    if message == 0: return False

    inv_s: int = invert(s, N)
    Q: Point = multiply(G, (message * inv_s) % N)
    R: Point = multiply(publicKey, (r * inv_s) % N)

    add(Q, R)
    return mod(Q.x, N) == r
    

if __name__ == '__main__':
    """
    [3, 116, 61, 190, 93, 174, 15, 154, 165, 22, 242, 56, 13, 168, 8, 194, 94,
    110, 224, 129, 237, 180, 216, 85, 221, 167, 203, 32, 104, 169, 181, 142, 159]
    """
    sk: List[int] = [
        17, 30, 0, 32, 247, 20, 162, 6, 47, 0, 31, 160, 16, 252, 180, 179, 136,
        24, 172, 113, 103, 72, 59, 104, 135, 229, 132, 209, 107, 129, 161, 171
    ]
    pk: List[int] = getPublicKey(sk, True)
    print(pk, len(pk))

    """
    x: 52577381964022070644701442866140528745228946117899238084264950131588662136479
    y: 9665905194987398137563352635586191466703234613099984357204279640613742434171
    """
    print(ArrToPoint(pk))

    msg: List[int] = [
        163, 51, 33, 249, 142, 79, 241, 194, 131, 199, 105, 152, 241, 79, 87, 68,
        117, 69, 211, 57, 179, 219, 83, 76, 109, 136, 109, 236, 180, 32, 159, 40
    ]
    entropy: List[int] = numToBytes(randint(0, P))
    sig: List[int] = sign(msg, sk, entropy)
    print(sig)

    isValid: bool = verify(sig, msg, pk)
    print(isValid)
