from util import joinBytes, splitBits
from typing import List


BIT_MASK: int = (1 << 32) - 1


# The first 32 bits of the fractional parts of the cube roots of the first 64 primes.
K: List[int] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]


def shaPad(message: List[int], byteSize: int) -> List[int]:
    bitSize: int = byteSize * 8
    outLength: int = (len(message) // bitSize + 1) * bitSize
    out: List[int] = [0] * outLength

    # Copy first 'n' values of 'message' to 'out'.
    i: int = 0
    while i < len(message):
        out[i] = message[i]
        i += 1

    # Append a single bit to the end of 'out'.
    out[i] = 0x80

    byteMask: int = (1 << 8) - 1
    inLength: int = len(message) * 8

    # Append a 'message' length to the end of 'out' in bits.
    i: int = len(out)
    while inLength:
        i -= 1
        out[i] = inLength & byteMask
        inLength >>= 8

    return out


def rotateRight(x: int, y: int) -> int:
    c0: int = x >> y
    c1: int = x << 32 - y
    return (c0 | c1) & BIT_MASK


def ch(x: int, y: int, z: int) -> int:
    c0: int = x & y
    c1: int = x ^ BIT_MASK
    c2: int = c1 & z
    return c0 ^ c2


def maj(x: int, y: int, z: int) -> int:
    c0: int = x & y
    c1: int = x & z
    c2: int = y & z
    return c0 ^ c1 ^ c2


def gamma(w: int, x: int, y: int, z: int) -> int:
    c0: int = rotateRight(w, x)
    c1: int = rotateRight(w, y)
    c2: int = w >> z
    return c0 ^ c1 ^ c2


def sigma(w: int, x: int, y: int, z: int) -> int:
    c0: int = rotateRight(w, x)
    c1: int = rotateRight(w, y)
    c2: int = rotateRight(w, z)
    return c0 ^ c1 ^ c2


def update(out: List[int], msg: List[int], start: int) -> None:
    W: List[int] = [0] * 64

    for i in range(16):
        W[i] = msg[start + i]

    for i in range(16, 64):
        g0: List[int] = gamma(W[i - 15], 7, 18, 3)
        g1: List[int] = gamma(W[i - 2], 17, 19, 10)
        W[i] = (W[i - 7] + W[i - 16] + g0 + g1) & BIT_MASK

    H: List[int] = [
        out[0], out[1], out[2], out[3],
        out[4], out[5], out[6], out[7]
    ]

    for i in range(len(W)):
        t0: int = (H[7] + sigma(H[4], 6, 11, 25) + ch(H[4], H[5], H[6]) + K[i] + W[i]) & BIT_MASK
        t1: int = (sigma(H[0], 2, 13, 22) + maj(H[0], H[1], H[2])) & BIT_MASK
        H[7] = H[6]
        H[6] = H[5]
        H[5] = H[4]
        H[4] = (t0 + H[3]) & BIT_MASK
        H[3] = H[2]
        H[2] = H[1]
        H[1] = H[0]
        H[0] = (t0 + t1) & BIT_MASK

    for i in range(len(H)):
        out[i] = (out[i] + H[i]) & BIT_MASK


def sha256(message: List[int]) -> List[int]:
    # The first 32 bits of the fractional parts of the square roots of the first 8 primes.
    H: List[int] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    padding: List[int] = shaPad(message, 8)     # Ensure 'message' length is evenly divisible by 64.
    payload: List[int] = joinBytes(padding, 4)  # Convert byte array to 32-bit array.

    # Use each 32 bit interval of 'message' to update 'H'.
    for i in range(0, len(payload), 16):
        update(H, payload, i)

    # Convert 32-bit array to byte array.
    return splitBits(H, 4)


def hmac256(key: List[int], message: List[int]) -> List[int]:
    if len(key) > 64:
        key = sha256(key)

    # Ensure 'key' length is evenly divisible by 64.
    padded: List[int] = [0] * 64
    for i in range(len(key)):
        padded[i] = key[i]

    # Xor each bit value of 'padded' and 0x36.
    for i in range(len(padded)):
        padded[i] ^= 0x36
    inner = padded + message

    # Xor each bit value of 'padded' and 0x6a.
    for i in range(len(padded)):
        padded[i] ^= 0x6a
    outer = padded + sha256(inner)

    return sha256(outer)


if __name__ == '__main__':
    seed: List[int] = [
        17, 30, 0, 32, 247, 20, 162, 6,
        47, 0, 31, 160, 16, 252, 180, 179,
        136, 24, 172, 113, 103, 72, 59, 104,
        135, 229, 132, 209, 107, 129, 161, 171
    ]

    message: List[int] = [
        116, 61, 190, 93, 174, 15, 154, 165,
        22, 242, 56, 13, 168, 8, 194, 94,
        110, 224, 129, 237, 180, 216, 85, 221,
        167, 203, 32, 104, 169, 181, 142, 159
    ]

    """
    [
        245, 193, 225, 252, 78, 189, 107, 65,
        212, 247, 154, 121, 76, 23, 200, 71,
        57, 11, 162, 77, 146, 114, 94, 245,
        167, 222, 51, 73, 246, 41, 166, 229
    ]
    """
    hashed: List[int] = sha256(seed)
    print(hashed)

    """
    [
        124, 138, 43, 183, 22, 113, 163, 106,
        2, 51, 104, 0, 189, 255, 149, 250,
        123, 137, 184, 6, 187, 185, 31, 172,
        96,  35, 248, 248, 160, 114, 94, 136
    ]
    """
    hmac: List[int] = hmac256(seed, message)
    print(hmac)