from util import joinBytes, splitBits
from typing import List


BIT_MASK: int = (1 << 64) - 1


# The first 64 bits of the fractional parts of the cube roots of the first 80 primes.
K: List[int] = [
    0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817
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
    c1: int = x << 64 - y
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
    W: List[int] = [0] * 80

    for i in range(16):
        W[i] = msg[start + i]

    for i in range(16, 80):
        g0: List[int] = gamma(W[i - 15], 1, 8, 7)
        g1: List[int] = gamma(W[i - 2], 19, 61, 6)
        W[i] = (W[i - 7] + W[i - 16] + g0 + g1) & BIT_MASK

    H: List[int] = [
        out[0], out[1], out[2], out[3],
        out[4], out[5], out[6], out[7]
    ]

    for i in range(len(W)):
        t0: int = (H[7] + sigma(H[4], 14, 18, 41) + ch(H[4], H[5], H[6]) + K[i] + W[i]) & BIT_MASK
        t1: int = (sigma(H[0], 28, 34, 39) + maj(H[0], H[1], H[2])) & BIT_MASK
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


def sha512(message: List[int]) -> List[int]:
    # The first 64 bits of the fractional parts of the square roots of the first 8 primes.
    H: List[int] = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]

    padding: List[int] = shaPad(message, 16)    # Ensure 'message' length is evenly divisible by 128.
    payload: List[int] = joinBytes(padding, 8)  # Convert byte array to 64-bit array.
    
    # Use each 64 bit interval of 'message' to update 'H'.
    for i in range(0, len(payload), 16):
        update(H, payload, i)

    # Convert 64-bit array to byte array.
    return splitBits(H, 8)


def hmac512(key: List[int], message: List[int]) -> List[int]:
    if len(key) > 128:
        key = sha512(key)

    # Ensure 'key' length is evenly divisible by 64.
    padded: List[int] = [0] * 128
    for i in range(len(key)):
        padded[i] = key[i]

    # Xor each bit value of 'padded' and 0x36.
    for i in range(len(padded)):
        padded[i] ^= 0x36
    inner = padded + message

    # Xor each bit value of 'padded' and 0x6a.
    for i in range(len(padded)):
        padded[i] ^= 0x6a
    outer = padded + sha512(inner)

    return sha512(outer)


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
        221, 25, 2, 226, 70, 121, 239, 173, 144, 234, 83, 139, 116, 37, 157, 110,
        115, 196, 251, 1, 172, 77, 47, 89, 55, 67, 231, 216, 84, 19, 14, 70,
        140, 201, 145, 143, 82, 118, 74, 45, 14, 146, 211, 6, 86, 12, 208, 33,
        60, 5, 6, 138, 80, 9, 111, 3, 237, 28, 21, 131, 88, 85, 223, 67
    ]
    """
    hashed: List[int] = sha512(seed)
    print(hashed)

    """
    [
        68, 111, 177, 106, 29, 143, 209, 146, 187, 67, 70, 130, 74, 237, 104, 186,
        86, 42, 101, 201, 91, 255, 7, 25, 50, 229, 150, 206, 44, 42, 154, 215,
        69, 249, 24, 0, 120, 252, 19, 232, 143, 83, 146, 21, 186, 2, 244, 159,
        105, 171, 250, 241, 11, 162, 232, 27, 64, 189, 203, 237, 74, 126, 54, 159
    ]
    """
    hmac: List[int] = hmac512(seed, message)
    print(hmac)