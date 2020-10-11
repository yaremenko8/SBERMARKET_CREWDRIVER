import os
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))


def cached(f, threshold=100):
    def g(*args, **kwargs):
        if g.cache == {}:
            if os.path.isfile(dir_path + '/cache/%s.cch' % f.__name__):
                fd = open(dir_path + '/cache/%s.cch' % f.__name__, "rb")
                g.cache = pickle.load(fd)
                fd.close()       
        if tuple(args) in g.cache:
            return g.cache[tuple(args)]
        res = f(*args, **kwargs)
        g.cache[tuple(args)] = res
        g.unsaved += 1
        if g.unsaved > threshold:
            fd = open(dir_path + '/cache/%s.cch' % f.__name__, "wb")
            pickle.dump(g.cache, fd)
            fd.close()
            g.unsaved = 0
        return res
    g.cache = {}
    g.unsaved = 0

    def force_dump():
        fd = open(dir_path + '/cache/%s.cch' % f.__name__, "wb")
        pickle.dump(g.cache, fd)
        fd.close()
    g.force_dump = force_dump

    def clear_cache(soft=False):
        g.cache = {}
        g.unsaved = 0
        if not soft:
            g.force_dump()
    g.clear_cache = clear_cache
    return g
