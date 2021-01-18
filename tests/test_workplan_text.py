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

"""Tests on export of work plan to text."""

from tasksched import workplan_to_text
from .utils import get_input_file


def test_workplan_to_text():
    """Test workplan_to_text function."""
    workplan = get_input_file('workplan_complete.yaml')
    text = workplan_to_text(workplan)
    assert '\x1b[0m' in text
    text = workplan_to_text(workplan, use_colors=False)
    assert ('Developer 1 > 2020-12-31   8d  89% ████▊██▊   '
            'task3, task2') in text
    assert ('Developer 2 > 2021-01-04   9d 100% ████▊█▊█▊  '
            'task3, task1, task2') in text
    text = workplan_to_text(workplan, use_colors=False, use_unicode=False)
    assert ('Developer 1 > 2020-12-31   8d  89% [xxx][x]   '
            'task3, task2') in text
    assert ('Developer 2 > 2021-01-04   9d 100% [xxx][][]  '
            'task3, task1, task2') in text

    workplan = get_input_file('workplan_complete2.yaml')
    text = workplan_to_text(workplan)
    assert '\x1b[0m' in text
    text = workplan_to_text(workplan, use_colors=False)
    assert 'Developer 1 > 2020-12-30   7d 100% ████▊█▊  task2, task1' in text
    assert 'Developer 2 > 2020-12-28   5d  71% ████▊    task3' in text
    assert 'Developer 3 > 2020-12-28   5d  71% ████▊    task3' in text
