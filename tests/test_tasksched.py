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


def test_merge_configs():
    """Test merge_configs function."""
    from tasksched import merge_configs

    # empty merge
    config = {}
    merge_configs(config, {})
    assert config == {}

    # update of dict
    config = {}
    merge_configs(config, {'test': {'key1': 1}})
    assert config == {'test': {'key1': 1}}
    merge_configs(config, {'test': {'key2': 2}})
    assert config == {'test': {'key1': 1, 'key2': 2}}
    merge_configs(config, {'test2': {'key3': 3}})
    assert config == {'test': {'key1': 1, 'key2': 2}, 'test2': {'key3': 3}}

    # update of list
    config = {}
    merge_configs(config, {'test': ['item1']})
    assert config == {'test': ['item1']}
    merge_configs(config, {'test': ['item2']})
    assert config == {'test': ['item1', 'item2']}
    merge_configs(config, {'test2': ['item3']})
    assert config == {'test': ['item1', 'item2'], 'test2': ['item3']}

    # update of string
    config = {'test': 'value'}
    merge_configs(config, {'test': 'new_value'})
    assert config == {'test': 'new_value'}

    # new key
    config = {'test': 'value'}
    merge_configs(config, {'new_test': 'new_value'})
    assert config == {'test': 'value', 'new_test': 'new_value'}

    # invalid: update of dict with a list
    config = {'test': {'key1': 1}}
    with pytest.raises(ValueError):
        merge_configs(config, {'test': ['item2']})

    # invalid: update of list with a dict
    config = {'test': ['item1']}
    with pytest.raises(ValueError):
        merge_configs(config, {'test': {'key2': 2}})


def test_main(monkeypatch):
    """Test main function."""
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
    """Test init function."""
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
