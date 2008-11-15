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
import codecs

import logging
logger = logging.getLogger('app.learn')

import tichy
import tichy.gui as gui
import tichy.style

from brain import Brain
from dic import Dic


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


class Answer(tichy.Application):

    def run(self, window, card, correct):
        self.name = "Correct" if correct else "Wrong"
        self.window = gui.Window(window, modal=True)
        frame = self.view(self.window)

        vbox = gui.Box(frame, axis=1)
        gui.Label(vbox, card.q, font_size=58)
        gui.Label(vbox, card.a)
        if card.comment:
            gui.Label(vbox, "(%s)" % card.comment)

        gui.Spring(vbox, axis=1)

        read_button = gui.Button(vbox)
        gui.Label(read_button, "Read")
        read_button.connect('clicked', self.on_read, card.a)

        next_button = gui.Button(vbox)
        gui.Label(next_button, "OK")

        yield tichy.tasklet.Wait(next_button, 'clicked')
        self.window.destroy()

    def on_read(self, b, msg):
        try:
            import subprocess
            espeak = 'espeak -s100 -vzh --stdout'
            cmd = "echo '%s' | %s | aplay" % (msg, espeak)
            logger.info("bash : %s", cmd)
            subprocess.Popen(cmd, shell=True)
        except Exception, e:
            logger.error("can't use espeak : %s" % e)


class Learn(tichy.Application):

    name = 'Learn'
    category = 'main/chinese'
    icon = 'icon.png'

    def run(self, window):
        self.window = gui.Window(window, modal=True)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)
        self.question_text = tichy.Text("Question")
        self.question_text.view(vbox, expand=True, font_size=58)

        self.choices = tichy.List()
        self.choices.view(vbox, expand=True)

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
        ret = yield tichy.WaitFirst(
            *[tichy.Wait(c, 'selected') for c in choices])
        ret = answers[ret[0]]
        if ret == card.a:
            # Correct answer
#             yield tichy.Dialog(self.window,
#                                "Correct", "%s : %s" %
#                                (card.a, card.comment or ''))
            yield Answer(self.window, card, True)
            yield True
        else:
            # yield tichy.Dialog(self.window, "Wrong Answer", "")
            yield Answer(self.window, card, False)
            yield False
