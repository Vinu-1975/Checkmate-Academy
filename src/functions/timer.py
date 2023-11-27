import time

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.6f ms' % \
              (f.__name__, args, kw, 1000*(te - ts)))
        return result

    return timed