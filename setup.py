#!/usr/bin/env python

#    Tichy
#
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

# from setuptools import setup, Extension
from distutils.core import setup
from distutils.extension import Extension
# from Cython.Distutils import build_ext
from glob import glob
import commands

# After too many troubles I decided to stop using cython in the build
# process from Cython.Distutils import build_ext


def plugins_files():
    """generate the plugins data files list

    It works by adding all the files ending with a set of specified
    extension to the data. So we have to be careful when adding files
    with new extension we have to add it here as well.
    """
    ret = []
    for root, dirs, files in os.walk('./test/plugins/'):
        if root.endswith('.svn'):
            dirs[:] = []
            continue
        # XXX: Where is the best place to put the plugins files ???
        dest = 'share/tichy/plugins/%s' % root[15:]
        src = []
        for file in files:
            if file.endswith((".py", ".ttf", ".png", ".dic", ".txt")):
                path = '%s/%s' % (root, file)
                src.append(path)
        ret.append((dest, src))
    return ret


def make_extension(name):
    """Create an extension for a given guic file
    """
    flags_map = {'-I': 'include_dirs', '-L': 'library_dirs',
                 '-l': 'libraries'}
    # I copied all this stuff from python-etk serup file I should do
    # it a better way. What we do here is parsing the output of
    # pkg-config to get the Extension arguments
    #
    # TODO: clean this
    cmdline = 'pkg-config --libs --cflags sdl'
    status, output = commands.getstatusoutput(cmdline)
    if status != 0:
        raise ValueError("could not find pkg-config module: sdl")
    kargs = {}
    for token in output.split():
        if token[:2] in flags_map:
            kargs.setdefault(flags_map[token[:2]], []).append(token[2:])
        else:
            kargs.setdefault("extra_compile_args", []).append(token)

    return Extension('%s' % name,
                     sources=['tichy/guic/%s.c' % name],
                     **kargs)


setup(name='Tichy',
      version='0.1',
      description='Python Applet Manager for OpenMoko',
      author="Guillaume 'charlie' Chereau",
      author_email='charlie@openmoko.org',
      # url='',
      packages = ['tichy', 'tichy.guic', 'tichy.guip',
                  'tichy.phone', 'tichy.prefs'],
      scripts= ['test/tichy'],
      # XXX: Those locations may not work on the neo !
      data_files = [('share/applications', ['data/tichy.desktop']),
                    ('share/pixmaps', ['data/tichy.png']),
                    ('share/tichy/pics', ['tichy/pics/sim.png'])] + \
          plugins_files(),
      ext_package='tichy.guic',
      ext_modules=[make_extension(x) for x in [
            'geo', 'cobject', 'widget', 'frame', 'painter', 'sdl_painter',
            'window', 'surf_widget', 'image']])
