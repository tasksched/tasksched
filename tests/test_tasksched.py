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

"""Tasksched tests."""

import io
import mock
import os
import pytest
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_main(monkeypatch):
    import tasksched

    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)

    # no action
    args = ['tasksched']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # display help
    args = ['tasksched', '--help']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # workplan, no input
    args = ['tasksched', 'workplan']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # workplan, file not found
    args = ['tasksched', 'workplan', 'unknown.json']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # workplan OK
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_complete.json')
    args = ['tasksched', 'workplan', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()

    # workplan, invalid JSON on input
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    args = ['tasksched', 'workplan']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # workplan, invalid JSON file
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_invalid.json')
    args = ['tasksched', 'workplan', filename]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # text workplan, missing resource
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_missing_resource.json')
    args = ['tasksched', 'text', filename]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # text workplan OK
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_complete.json')
    args = ['tasksched', 'text', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()


def test_init(monkeypatch):
    import tasksched
    stdin = io.StringIO('{}')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_complete.json')
    args = ['tasksched', 'workplan', filename]
    with mock.patch.object(tasksched, 'main', return_value=0):
        with mock.patch.object(tasksched, '__name__', '__main__'):
            with mock.patch.object(sys, 'argv', args):
                tasksched.init(force=True)
