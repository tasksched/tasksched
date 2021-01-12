#!/usr/bin/env python3
#
# Copyright (C) 2020-2021 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of Tasksched.
#
# Tasksched is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Tasksched is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tasksched.  If not, see <https://www.gnu.org/licenses/>.
#

"""Tasksched utility functions for tests."""

import os

import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_input_file(filename, raw=False):
    """
    Read a YAML/JSON file.

    :param str filename: filename
    :param bool raw: if True, return the file as string
    :rtype: dict
    :return: input file as dict (or as string if raw == True)
    """
    path = os.path.join(TESTS_DIR, filename)
    with open(path) as _file:
        if raw:
            return _file.read()
        return yaml.safe_load(_file)
