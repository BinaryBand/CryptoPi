from typing import List


# Convert number array to large int.
def bytesToNum(arr: List[int], endian='be') -> int:
    n: int = 0

    if endian == 'be':
        for a in arr:
            n = n << 8 | a
    else:
        for i, a in enumerate(arr):
            n += a << (8 * i)

    return n


def numToBytes(n: int, byteSize: int = 32, endian='be') -> List[int]:
    byteMask: int = (1 << 8) - 1
    out: List[int] = [0] * byteSize

    while n:
        byteSize -= 1
        curr: int = n & byteMask
        out[byteSize] = curr
        n >>= 8

    return out if endian == 'be' else out[::-1]


def joinBytes(msg: List[int], numBytes: int) -> List[int]:
    outLength: int = int(len(msg) // numBytes)
    out: List[int] = [0] * outLength

    for i in range(outLength):
        k: int = i * numBytes
        chunk: List[int] = msg[k: k + numBytes]
        out[i] = bytesToNum(chunk)

    return out


def splitBits(msg: List[int], byteSize: int) -> List[int]:
    inLength: int = len(msg)
    outLength: int = inLength * byteSize
    out: List[int] = [0] * outLength

    for i in range(inLength):
        m: int = msg[i]

        for k in range(byteSize):
            offset: int = i * byteSize
            shift: int = byteSize * 8 - (k + 1) * 8
            out[k + offset] = (m >> shift) & 0xff

    return out
