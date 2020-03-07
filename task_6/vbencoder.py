from struct import pack, unpack
from typing import List


def vb_encode_num(num: int) -> bytes:
    bytes_list = []

    while True:
        bytes_list.insert(0, num % 128)

        if num < 128:
            break
        num = num // 128

    bytes_list[-1] += 128

    return pack(f'{len(bytes_list)}B', *bytes_list)


def vb_encode(nums: List[int]) -> bytes:
    bytes_list = []

    for num in nums:
        bytes_list.append(vb_encode_num(num))

    return b''.join(bytes_list)


def vb_decode(bytestream: bytes) -> List[int]:
    n = 0
    nums = []
    bytestream = unpack(f'{len(bytestream)}B', bytestream)

    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            nums.append(n)
            n = 0

    return nums


def preprocess_postings(postings: List[int]) -> List[int]:
    base = postings[0]
    postings = postings[1:]

    for index, posting in enumerate(postings):
        postings[index] = posting - base
    postings.insert(0, base)

    return postings
