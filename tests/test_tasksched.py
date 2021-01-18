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

"""Tasksched tests."""

import io
import os
import sys

import mock
import pytest

import tasksched

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_load_config():  # pylint: disable=too-many-statements
    """Test load_config function."""
    # empty merge (no data)
    config1 = io.StringIO('')
    config2 = io.StringIO('')
    config = tasksched.load_config([config1, config2])
    assert config == {}

    # empty merge (empty JSON)
    config1 = io.StringIO('{}')
    config2 = io.StringIO('{}')
    config = tasksched.load_config([config1, config2])
    assert config == {}

    # update of string
    config1 = io.StringIO('{"test": "value"}')
    config2 = io.StringIO('{"test": "new_value"}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': 'new_value'}

    # new key
    config1 = io.StringIO('{"test": "value"}')
    config2 = io.StringIO('{"new_test": "new_value"}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': 'value', 'new_test': 'new_value'}

    # update of dict
    config1 = io.StringIO('{}')
    config2 = io.StringIO('{"test": {"key1": 1}}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': {'key1': 1}}

    config1 = io.StringIO('{"test": {"key1": 1}}')
    config2 = io.StringIO('{"test": {"key2": 2}}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': {'key1': 1, 'key2': 2}}

    config1 = io.StringIO('{"test": {"key1": 1}}')
    config2 = io.StringIO('{"test2": {"key3": 3}}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': {'key1': 1}, 'test2': {'key3': 3}}

    # update of list of strings
    config1 = io.StringIO('{"test": ["item1"]}')
    config2 = io.StringIO('{"test": ["item2"]}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': ['item1', 'item2']}

    # update of list of dicts without id
    config1 = io.StringIO('{"test": [{"name": "first"}]}')
    config2 = io.StringIO('{"test": [{"name": "second"}]}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': [{'name': 'first'}, {'name': 'second'}]}

    # update of list of dicts with id
    config1 = io.StringIO('{"test": [{"id": "1", "name": "first"}]}')
    config2 = io.StringIO('{"test": [{"id": "2", "name": "second"}]}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': [{'id': '1', 'name': 'first'},
                               {'id': '2', 'name': 'second'}]}

    config1 = io.StringIO('{"test": [{"id": "1", "name": "first"}]}')
    config2 = io.StringIO('{"test": [{"id": "1", "name": "first again"}]}')
    config = tasksched.load_config([config1, config2])
    assert config == {'test': [{'id': '1', 'name': 'first again'}]}

    # invalid: update of dict with a list
    config1 = io.StringIO('{"test": {"key1": 1}}')
    config2 = io.StringIO('{"test": ["key2"]}')
    with pytest.raises(ValueError):
        config = tasksched.load_config([config1, config2])

    # invalid: update of list with a dict
    config1 = io.StringIO('{"test": ["key1"]}')
    config2 = io.StringIO('{"test": {"key2": 2}}')
    with pytest.raises(ValueError):
        config = tasksched.load_config([config1, config2])


def test_main(monkeypatch):  # pylint: disable=too-many-statements
    """Test main function."""
    stdin = io.StringIO('')
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

    # action: workplan, no input
    args = ['tasksched', 'workplan']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: workplan, file not found
    args = ['tasksched', 'workplan', 'unknown.yaml']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: workplan, OK
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_complete.yaml')
    args = ['tasksched', 'workplan', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()

    # action: workplan as JSON, OK
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_complete.yaml')
    args = ['tasksched', 'workplan', '--json', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()

    # action: workplan, invalid YAML on input
    stdin = io.StringIO('{')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    args = ['tasksched', 'workplan']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: workplan, invalid YAML file
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_invalid.yaml')
    args = ['tasksched', 'workplan', filename]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: text, no input
    args = ['tasksched', 'text']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            with mock.patch.object(sys.stdin, 'isatty', lambda: True):
                tasksched.main()

    # action: text, missing tasks
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_missing_tasks.yaml')
    args = ['tasksched', 'text', filename]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: text, OK
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_complete.yaml')
    args = ['tasksched', 'text', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()

    # action: html, no input
    args = ['tasksched', 'html']
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            with mock.patch.object(sys.stdin, 'isatty', lambda: True):
                tasksched.main()

    # action: html, missing tasks
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_missing_tasks.yaml')
    args = ['tasksched', 'html', filename]
    with pytest.raises(SystemExit):
        with mock.patch.object(sys, 'argv', args):
            tasksched.main()

    # action: html, OK
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'workplan_complete.yaml')
    args = ['tasksched', 'html', filename]
    with mock.patch.object(sys, 'argv', args):
        tasksched.main()


def test_init(monkeypatch):
    """Test init function."""
    stdin = io.StringIO('')
    stdin.fileno = lambda: 0
    monkeypatch.setattr('sys.stdin', stdin)
    filename = os.path.join(TESTS_DIR, 'project_complete.yaml')
    args = ['tasksched', 'workplan', filename]
    with mock.patch.object(tasksched, 'main', return_value=0):
        with mock.patch.object(tasksched, '__name__', '__main__'):
            with mock.patch.object(sys, 'argv', args):
                tasksched.init(force=True)
