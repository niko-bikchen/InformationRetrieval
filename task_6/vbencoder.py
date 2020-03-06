from struct import pack, unpack


def vb_encode_num(num: int):
    bytes_list = []

    while True:
        bytes_list.insert(0, num % 128)

        if num < 128:
            break
        num = num // 128

    bytes_list[-1] += 128

    return pack(f'{len(bytes_list)}B', *bytes_list)


def vb_encode(nums: list):
    bytes_list = []

    for num in nums:
        bytes_list.append(vb_encode_num(num))

    return b''.join(bytes_list)


def vb_decode(bytestream: bytes):
    n: int = 0
    nums: list = []
    bytestream = unpack(f'{len(bytestream)}B', bytestream)

    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            nums.append(n)
            n = 0

    return nums
