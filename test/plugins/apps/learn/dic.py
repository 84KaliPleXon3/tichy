from random import choice

from card import Card

class Dic(list):
    def read(file):
        ret = Dic()
        for line in file:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            ret.append(Card.read(line))
        return ret
    read = staticmethod(read)

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(Dic, self).__getitem__(key)
        for c in self:
            if c.q == key:
                return c
        raise KeyError("can't find card %s" % key)

    def get(self):
        ret = choice(self)
        self.remove(ret)
        return ret
        
    def append(self, card):
        for c in self:
            if c.q == card.q:
                raise "card %s already in the dict" % c.q
        super(Dic, self).append(card)
        
    def remove(self, value):
        if isinstance(value, Card):
            value = value.q
        if isinstance(value, unicode):
            for v in self:
                if v.q == value:
                    value = v
                    break
        super(Dic, self).remove(value)
