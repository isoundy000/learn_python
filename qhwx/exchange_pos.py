
def b(pos, cid):
    if cid in a:
        a[a.index(cid)] = 0
    a[pos - 1] = cid
    return a


if __name__ == '__main__':
    a = [0, 0, 0, 0, -1, -1, -1, -1]
    b(1, 1005)
    print a
    b(2, 1006)
    print a
    b(2, 1007)
    print a
    b(1, 1006)
    print a
    b(1, 1007)
    print a
    b(2, 1005)
    b(3, 1006)
    b(3, 1007)
    print a