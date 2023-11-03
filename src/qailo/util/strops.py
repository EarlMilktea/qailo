def binary2str(n, i):
    return bin(i)[2:].zfill(n)


def str2binary(s):
    n = len(s)
    c = 0
    for i in range(n):
        assert s[i] == "0" or s[i] == "1"
        if s[i] == "1":
            c += 2 ** (n - i - 1)
    return c
