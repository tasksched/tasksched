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

"""Tests on export of work plan to HTML."""

from tasksched import workplan_to_html
from .utils import get_input_file


def test_workplan_to_html():
    """Test workplan_to_html function."""
    workplan = get_input_file('workplan_complete.yaml')
    html = workplan_to_html(workplan)
    assert html.startswith('<!doctype html>')

    workplan = get_input_file('workplan_complete2.yaml')
    html = workplan_to_html(workplan)
    assert html.startswith('<!doctype html>')
