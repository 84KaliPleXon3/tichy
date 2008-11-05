# -*- coding: utf-8 -*-
#    Tichy
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.

import random

import tichy
import tichy.gui as gui
import tichy.style

from brain import Brain
from dic import Dic

import codecs

import logging
logger = logging.getLogger('App.Learn')


class Choice(tichy.Item):
    def __init__(self, value):
        self.value = value
    def view(self, parent):
        ret = gui.Button(parent)
        gui.Label(ret, self.value)
        
        def on_clicked(b):
            self.emit('selected')
        ret.connect('clicked', on_clicked)
        
        return ret

class Learn(tichy.Application):
    name = 'Learn'
    category = 'general'
    icon = 'icon.png'
     
    def run(self, window):
        self.window = gui.Window(window, modal = True)   # We run into a new modal window
        frame = self.view(self.window, back_button=True)
        
        vbox = gui.Box(frame, axis = 1)
        self.question_text = tichy.Text("Question")
        self.question_text.view(vbox, expandable = True)
        
        self.choices = tichy.List()
        self.choices.view(vbox)
        
        frame.connect('back', self.on_quit)
        
        dic = codecs.open(Learn.path('characters.dic'), encoding='utf-8')
        
        logger.info("opening the dict")
        # dic = open(Learn.path('characters.dic'), 'r')
        dic = Dic.read(dic)
        self.full_dic = dic[:]
        brain = Brain()
        
        logger.info("start game")
        self.task = None
        while True:
            self.task = brain.ask(self.ask, dic)
            try:
                yield self.task
            except GeneratorExit:
                break
                
        self.window.destroy()
        yield None
        
    def on_quit(self, *args):
        self.task.exit()
    
    @tichy.tasklet.tasklet
    def ask(self, card, level):
        logger.info("ask")
        question = card.q
        
        logger.info("generate answers set")
        # We also use 3 random value from the dict
        rand_answers = [random.choice(self.full_dic).a for i in range(3)]
        answers = rand_answers + [card.a]
        random.shuffle(answers)
        
        self.question_text.value = question
        self.choices.clear()
        
        choices = [Choice(a) for a in answers]
        
        for c in choices:
            self.choices.append(c)
        
        logger.info("wait for answer")
        ret = yield tichy.WaitFirst(*[tichy.Wait(c, 'selected') for c in choices])
        ret = answers[ret[0]]
        if ret == card.a:
            # Correct answer
            yield tichy.Message(self.window, "Correct", "%s : %s" % (card.a, card.comment or ''))
            yield True
        else:
            yield tichy.Message(self.window, "Wrong Answer", "")
            yield False
        
