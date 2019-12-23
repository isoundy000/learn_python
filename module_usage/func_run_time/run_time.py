def main():
    import time
    a = range(10000)
    b = range(500)
    c = time.time()
    print max(list(set(a) - set(b)))
    d = time.time()
    exec_time = (d - c) * 1000
    print "%.3f s" % (d - c) if exec_time >= 1000 else "%.3f ms" % exec_time


if __name__ == '__main__':
    main()