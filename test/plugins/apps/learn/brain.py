from card import Card
from StringIO import StringIO

from box import Box

from tichy.tasklet import Wait, Tasklet, WaitFirst, tasklet

class Brain(list):
    def __init__(self, size = 10):
        for n in range(size):
            self.append(Box(2**n))

    def write(self, file):
        print >>file, len(self)
        [b.write(file) for b in self]

    def __repr__(self):
        ret = StringIO()
        self.write(ret)
        return ret.getvalue()

    def read(file, dic):
        # The first line is the number of boxes
        line = file.readline().strip()
        s = int(line)
        ret = Brain(0)
        for b in xrange(s):
            ret.append(Box.read(file, dic))
        return ret
    read = staticmethod(read)

    @tasklet
    def ask(self, ask, dic = None):
        if not dic:
            dic = self
        # we start from the top, if there is a full box
        # we try to raise on card
        # 
        #for n, b in reversed(list(enumerate(self))):
        l = list(enumerate(self))
        l.reverse()
        for n, b in l:
            if b.full():
                c = b.pop(0)
                r = yield ask(c, n)
                if r:
                    self[n+1].append(c)
                else:
                    self[0].append(c)
                return

        # if there is no full box, then we had a card
        self[0].append(dic.get())
        ret = yield self.ask(ask, dic)

        
    def cards(self):
        """Generate all the card in the brain"""
        for b in self:
            for c in b:
                yield c


    def get(self):
        l = self[:]
        l.reverse()
        for b in l:
            if b:
                return b.pop(0)
        raise ValueError("Empty brain")
