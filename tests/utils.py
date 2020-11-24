#!/usr/bin/env python3
#
# Copyright (C) 2020 Sébastien Helleu <flashcode@flashtux.org>
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

import json
import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_json_file(filename):
    """
    Reads a JSON file.

    :param str filename: JSON filename
    :rtype: dict
    :return: JSON data
    """
    path = os.path.join(TESTS_DIR, filename)
    with open(path) as json_file:
        return json.load(json_file)
