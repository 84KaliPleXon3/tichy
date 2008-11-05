from card import Card

class Box(list):
    def __init__(self, size):
        self.size = size

    def __repr__(self):
        ret = StringIO()
        self.write(ret)
        return ret.getvalue()

    def write(self, file):
        print >>file, "%i/%i" % (len(self), self.size)
        for c in self:
            print >>file, c.q

    def full(self):
        return len(self) >= self.size

    def append(self, c):
        assert not self.full()
        super(Box, self).append(c)

    def read(file, dic):
        l, s = [int(x) for x in file.readline().split("/")]
        ret = Box(s)
        for c in xrange(l):
            q = file.readline().strip()
            ret.append(dic[q])
        return ret
    read = staticmethod(read)
