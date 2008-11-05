import re

class Card(object):
    def __init__(self, q, a, comment = None):
        self.q = q
        self.a = a
        self.comment = comment

    def __repr__(self):
        return '%s -> %s' % (self.q, self.a)

    reg = re.compile(
        r"\s*(.*?)\s*"  \
        r"->\s*(.*?)\s*"  \
        r"(?:\[(.*)\])?\s*$"
    )

    def read(line):
        ret = Card.reg.match(line)
        q,a,c = ret.group(1,2,3)
        return Card(q,a,c)
    read = staticmethod(read)        
