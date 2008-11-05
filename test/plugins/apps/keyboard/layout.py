from tichy.key import *
from tichy import gui
import tichy.item as item
from tichy.gui import Vect

class Key(item.Item):
    def __init__(self, text, key, mod, unicode, rect):
        super(Key, self).__init__()
        self.key = key
        self.mod = mod
        self.unicode = unicode
        self.text = text
        self.rect = rect


    def _view(self, parent, size, pos, same_as = None):
        ret = gui.Button(parent, item=self, min_size=size, optimal_size=size, pos=pos, same_as=same_as)
        # If we provided a widget for optimization,
        # then we can also use the widget child for next view
        if same_as is not None:
            same_as = same_as.children[0]
        gui.Label(ret, self.text, min_size=size, optimal_size=size, same_as=same_as)
        return ret

    def view(self, parent, same_as = None):
        size = Vect(self.rect[2] * 56, self.rect[3] * 56)
        pos = Vect(self.rect[0] * 56, self.rect[1] * 56)
        ret = self._view(parent, size, pos, same_as)
        return ret

class SpecialKey(Key):
    def __init__(self, *args):
        super(SpecialKey, self).__init__(*args) 
        self.actor = None

    def _view(self, parent, size, pos, same_as = None):
        self.actor = self.create_actor()
        ret = self.actor.view(parent, min_size=size, optimal_size=size,
                              pos=pos, same_as=same_as)
        return ret

    def get_name(self): return self.text

    def set_name(self, x): pass

    name = property(get_name, set_name)


class Layout(object):
    def __init__(self, name, keys):
        self.name = name
        self.keys = []
        for k in keys:
            if isinstance(k[1], SpecialKeys):
                self.keys.append(SpecialKey(*k))
                continue
            self.keys.append(Key(*k))

lowercase_layout = Layout('abc',[
    ('a', K_a, 0, 'a', (0,0,1,1) ),
    ('b', K_b, 0, 'b', (1,0,1,1) ),
    ('c', K_c, 0, 'c', (2,0,1,1) ),
    ('d', K_d, 0, 'd', (3,0,1,1) ),
    ('e', K_e, 0, 'e', (4,0,1,1) ),
    ('f', K_f, 0, 'f', (5,0,1,1) ),
    ('g', K_g, 0, 'g', (6,0,1,1) ),
    ('h', K_h, 0, 'h', (7,0,1,1) ),
    ('i', K_i, 0, 'i', (0,1,1,1) ),
    ('j', K_j, 0, 'j', (1,1,1,1) ),
    ('k', K_k, 0, 'k', (2,1,1,1) ),
    ('l', K_l, 0, 'l', (3,1,1,1) ),
    ('m', K_m, 0, 'm', (4,1,1,1) ),
    ('n', K_n, 0, 'n', (5,1,1,1) ),
    ('o', K_o, 0, 'o', (6,1,1,1) ),
    ('p', K_p, 0, 'p', (7,1,1,1) ),
    ('q', K_q, 0, 'q', (0,2,1,1) ),
    ('r', K_r, 0, 'r', (1,2,1,1) ),
    ('s', K_s, 0, 's', (2,2,1,1) ),
    ('t', K_t, 0, 't', (3,2,1,1) ),
    ('u', K_u, 0, 'u', (4,2,1,1) ),
    ('v', K_v, 0, 'v', (5,2,1,1) ),
    ('w', K_w, 0, 'w', (6,2,1,1) ),
    ('x', K_x, 0, 'x', (7,2,1,1) ),
    ('y', K_y, 0, 'y', (0,3,1,1) ),
    ('z', K_z, 0, 'z', (1,3,1,1) ),
    ('.', K_PERIOD, 0, '.', (2,3,1,1) ),
    (' ', K_SPACE, 0, ' ', (3,3,1,1) ),
    ('ret', K_RETURN, 0, '\n', (4,3,1,1) ),
    ('del', K_BACKSPACE, 0, '', (5,3,1,1) ),
    ('switch', K_SWITCH_LAYOUT, 0, '', (6,3,2,1) )
])

uppercase_layout = Layout('ABC',[
    ('A', K_a, 1, 'A', (0,0,1,1) ),
    ('B', K_b, 1, 'B', (1,0,1,1) ),
    ('C', K_c, 1, 'C', (2,0,1,1) ),
    ('D', K_d, 1, 'D', (3,0,1,1) ),
    ('E', K_e, 1, 'E', (4,0,1,1) ),
    ('F', K_f, 1, 'F', (5,0,1,1) ),
    ('G', K_g, 1, 'G', (6,0,1,1) ),
    ('H', K_h, 1, 'H', (7,0,1,1) ),
    ('I', K_i, 1, 'I', (0,1,1,1) ),
    ('J', K_j, 1, 'J', (1,1,1,1) ),
    ('K', K_k, 1, 'K', (2,1,1,1) ),
    ('L', K_l, 1, 'L', (3,1,1,1) ),
    ('M', K_m, 1, 'M', (4,1,1,1) ),
    ('N', K_n, 1, 'N', (5,1,1,1) ),
    ('O', K_o, 1, 'O', (6,1,1,1) ),
    ('P', K_p, 1, 'P', (7,1,1,1) ),
    ('Q', K_q, 1, 'Q', (0,2,1,1) ),
    ('R', K_r, 1, 'R', (1,2,1,1) ),
    ('S', K_s, 1, 'S', (2,2,1,1) ),
    ('T', K_t, 1, 'T', (3,2,1,1) ),
    ('U', K_u, 1, 'U', (4,2,1,1) ),
    ('V', K_v, 1, 'V', (5,2,1,1) ),
    ('W', K_w, 1, 'W', (6,2,1,1) ),
    ('X', K_x, 1, 'X', (7,2,1,1) ),
    ('Y', K_y, 1, 'Y', (0,3,1,1) ),
    ('Z', K_z, 1, 'Z', (1,3,1,1) ),
    ('.', K_PERIOD, 0, '.', (2,3,1,1) ),
    (' ', K_SPACE, 0, ' ', (3,3,1,1) ),
    ('ret', K_RETURN, 0, '\n', (4,3,1,1) ),
    ('del', K_BACKSPACE, 0, '', (5,3,1,1) ),
    ('switch', K_SWITCH_LAYOUT, 0, '', (6,3,2,1) )
])

number_layout = Layout('123',[
    ('1', K_1, 0, '1', (0,0,1,1) ),
    ('2', K_2, 0, '2', (1,0,1,1) ),
    ('3', K_3, 0, '3', (2,0,1,1) ),
    ('4', K_4, 0, '4', (0,1,1,1) ),
    ('5', K_5, 0, '5', (1,1,1,1) ),
    ('6', K_6, 0, '6', (2,1,1,1) ),
    ('7', K_7, 0, '7', (0,2,1,1) ),
    ('8', K_8, 0, '8', (1,2,1,1) ),
    ('9', K_9, 0, '9', (2,2,1,1) ),
    ('0', K_0, 0, '0', (1,3,1,1) ),
    
    ('*', K_KP_MULTIPLY, 0, '*', (3,0,1,1) ),
    ('+', K_KP_PLUS, 0, '+', (3,1,1,1) ),
    ('#', K_HASH, 0, '#', (3,2,1,1) ),
    
    ('ret', K_RETURN, 0, '\n', (4,3,1,1) ),
    ('del', K_BACKSPACE, 0, '', (5,3,1,1) ),

    ('switch', K_SWITCH_LAYOUT, 0, '', (6,3,2,1) )
])


punctuation_layout = Layout('?!(',[
    ('?', K_QUESTION, 0, '?', (0,0,1,1) ),
    ('!', K_EXCLAIM, 0, '!', (1,0,1,1) ),
    (',', K_COMMA, 0, ',', (2,0,1,1) ),
    ('"', K_QUOTEDBL, 0, '"', (3,0,1,1) ),
    (':', K_COLON, 0, ':', (4,0,1,1) ),
    (';', K_SEMICOLON, 0, ';', (5,0,1,1) ),
    ('<', K_LESS, 0, '<', (6,0,1,1) ),
    ('=', K_EQUALS, 0, '=', (7,0,1,1) ),
    ('>', K_GREATER, 0, '>', (0,1,1,1) ),
    ('(', K_LEFTPAREN, 0, '(', (1,1,1,1) ),
    (')', K_RIGHTPAREN, 0, ')', (2,1,1,1) ),
    ('@', K_AT, 0, '@', (3,1,1,1) ),
    ('#', K_HASH, 0, '#', (4,1,1,1) ),
    ('$', K_DOLLAR, 0, '$', (5,1,1,1) ),
    ('*', K_ASTERISK, 0, '*', (6,1,1,1) ),
    ('+', K_PLUS, 0, '+', (7,1,1,1) ),
    ('-', K_MINUS, 0, '-', (0,2,1,1) ),
    ('\'', K_QUOTE, 0, '\'', (1,2,1,1) ),
    ('[', K_LEFTBRACKET, 0, '[', (2,2,1,1) ),
    (']', K_RIGHTBRACKET, 0, 't', (3,2,1,1) ),
    ('&', K_AMPERSAND, 0, '&', (4,2,1,1) ),
    ('_', K_UNDERSCORE, 0, '_', (5,2,1,1) ),
    ('/', K_KP_DIVIDE, 0, '/', (6,2,1,1) ),
    ('.', K_KP_PERIOD, 0, '.', (7,2,1,1) ),
    ('^', K_CARET, 0, '^', (0,3,1,1) ),
    (' ', K_SPACE, 0, ' ', (1,3,1,1) ),
    ('ret', K_RETURN, 0, '\n', (2,3,2,1) ),
    ('del', K_BACKSPACE, 0, '', (4,3,2,1) ),
    ('switch', K_SWITCH_LAYOUT, 0, '', (6,3,2,1) )
])

