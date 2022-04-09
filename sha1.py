from util import joinBytes, splitBits
from typing import List


BIT_MASK: int = (1 << 32) - 1


# The first 32 bits of the fractional parts of the cube roots of the first 4 primes.
K: List[int] = [0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6]


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


def ft(s: int, x: int, y: int, z: int) -> int:
  if s == 0: return ch(x, y, z)
  if s == 1 or s == 3: return x ^ y ^ z
  if s == 2: return maj(x, y, z) 


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
    W: List[int] = [0] * 80

    for i in range(16):
        W[i] = msg[start + i]

    for i in range(16, 80):
        c: int = W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16]
        W[i] = rotateRight(c, 31)

    H: List[int] = [out[0], out[1], out[2], out[3], out[4]]

    for i in range(len(W)):
        s: int = i // 20
        t: int = (rotateRight(H[0], 27) + ft(s, H[1], H[2], H[3]) + H[4] + W[i] + K[s]) & BIT_MASK
        H[4] = H[3]
        H[3] = H[2]
        H[2] = rotateRight(H[1], 2)
        H[1] = H[0]
        H[0] = t

    for i in range(len(H)):
        out[i] = (out[i] + H[i]) & BIT_MASK


def sha1(message: List[int]) -> List[int]:
    # The first 32 bits of the fractional parts of the square roots of the first 5 primes.
    H: List[int] = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]

    padding: List[int] = shaPad(message, 8)     # Ensure 'message' length is evenly divisible by 64.
    payload: List[int] = joinBytes(padding, 4)  # Convert byte array to 32-bit array.

    # Use each 32 bit interval of 'message' to update 'H'.
    for i in range(0, len(payload), 16):
        update(H, payload, i)

    # Convert 32-bit array to byte array.
    return splitBits(H, 4)


def hmac1(key: List[int], message: List[int]) -> List[int]:
    if len(key) > 64:
        key = sha1(key)

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
    outer = padded + sha1(inner)

    return sha1(outer)


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
        80, 157, 238, 228, 93, 168, 13, 36, 154, 30,
        202, 232, 182, 73, 69, 143, 109, 73, 59, 153
    ]
    """
    hashed: List[int] = sha1(seed)
    print(hashed)

    """
    [
        226, 250, 216, 40, 236, 216, 81, 102, 19, 54,
        185, 126, 89, 122, 19, 60, 196, 149, 62, 22
    ]
    """
    hmac: List[int] = hmac1(seed, message)
    print(hmac)