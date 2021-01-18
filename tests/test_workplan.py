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

"""Tasksched work plan tests."""

from datetime import date

import pytest

from tasksched import (
    build_workplan,
    Project,
    WorkPlan,
    yaml_dump,
)
from .utils import get_input_file


def test_workplan():
    """Test WorkPlan class."""
    with pytest.raises(TypeError):
        WorkPlan()  # pylint: disable=no-value-for-parameter
    project = Project(get_input_file('project_complete.yaml'))
    workplan = WorkPlan(project)
    assert workplan.remaining == 0
    assert workplan.duration == 10
    assert workplan.end_date == date(2021, 1, 5)
    assert workplan.resources_use == 85.0
    assert workplan.project.resources[0].assigned == [
        {
            'task': 'task3',
            'duration': 10,
        },
    ]
    assert workplan.project.resources[0].assigned_tasks == [
        {
            'id': 'task3',
            'title': 'The third task',
        },
    ]
    assert workplan.project.resources[0].duration == 10
    assert workplan.project.resources[0].end_date == date(2021, 1, 5)
    assert workplan.project.resources[0].use == 100
    assert workplan.project.resources[1].assigned == [
        {
            'task': 'task2',
            'duration': 5,
        },
        {
            'task': 'task1',
            'duration': 2,
        },
    ]
    assert workplan.project.resources[1].assigned_tasks == [
        {
            'id': 'task2',
            'title': 'The second task',
        },
        {
            'id': 'task1',
            'title': 'The first task',
        },
    ]
    assert workplan.project.resources[1].duration == 7
    assert workplan.project.resources[1].end_date == date(2020, 12, 30)
    assert workplan.project.resources[1].use == 70
    assert workplan.project.tasks[0].remaining == 0
    assert workplan.project.tasks[1].remaining == 0
    assert workplan.project.tasks[2].remaining == 0


def test_workplan_split_2():
    """Test WorkPlan class with split of tasks into 2."""
    workplan = WorkPlan(Project(get_input_file('project_complete.yaml')),
                        {'task3': 2, 'task2': 2})
    assert workplan.project.tasks[0].task_id == 'task1'
    assert workplan.project.tasks[0].title == 'The first task'
    assert workplan.project.tasks[0].duration == 2
    assert workplan.project.tasks[1].task_id == 'task2'
    assert workplan.project.tasks[1].title == 'The second task (1/2)'
    assert workplan.project.tasks[1].duration == 3
    assert workplan.project.tasks[2].task_id == 'task2'
    assert workplan.project.tasks[2].title == 'The second task (2/2)'
    assert workplan.project.tasks[2].duration == 2
    assert workplan.project.tasks[3].task_id == 'task3'
    assert workplan.project.tasks[3].title == 'The third task (1/2)'
    assert workplan.project.tasks[3].duration == 5
    assert workplan.project.tasks[4].task_id == 'task3'
    assert workplan.project.tasks[4].title == 'The third task (2/2)'
    assert workplan.project.tasks[4].duration == 5


def test_workplan_split_3():
    """Test WorkPlan class with split of tasks into 3."""
    project = Project(get_input_file('project_complete.yaml'))
    project.tasks[1].max_resources = 3
    workplan = WorkPlan(project, {'task2': 3})
    assert workplan.project.tasks[0].task_id == 'task1'
    assert workplan.project.tasks[0].title == 'The first task'
    assert workplan.project.tasks[0].duration == 2
    assert workplan.project.tasks[1].task_id == 'task2'
    assert workplan.project.tasks[1].title == 'The second task (1/3)'
    assert workplan.project.tasks[1].duration == 2
    assert workplan.project.tasks[2].task_id == 'task2'
    assert workplan.project.tasks[2].title == 'The second task (2/3)'
    assert workplan.project.tasks[2].duration == 2
    assert workplan.project.tasks[3].task_id == 'task2'
    assert workplan.project.tasks[3].title == 'The second task (3/3)'
    assert workplan.project.tasks[3].duration == 1
    assert workplan.project.tasks[4].task_id == 'task3'
    assert workplan.project.tasks[4].title == 'The third task'
    assert workplan.project.tasks[4].duration == 10


def test_build_workplan():
    """Test build_workplan function."""
    workplan = build_workplan(Project(get_input_file('project_complete.yaml')))
    assert workplan.remaining == 0
    assert workplan.duration == 9
    assert workplan.end_date == date(2021, 1, 4)
    assert workplan.resources_use == 94.44444444444444
    assert workplan.project.resources[0].assigned == [
        {
            'task': 'task3',
            'duration': 5,
        },
        {
            'task': 'task2',
            'duration': 3,
        },
    ]
    assert workplan.project.resources[0].assigned_tasks == [
        {
            'id': 'task3',
            'title': 'The third task (1/2)',
        },
        {
            'id': 'task2',
            'title': 'The second task (1/2)',
        },
    ]
    assert workplan.project.resources[0].duration == 8
    assert workplan.project.resources[0].end_date == date(2020, 12, 31)
    assert workplan.project.resources[0].use == 88.88888888888889
    assert workplan.project.resources[1].assigned == [
        {
            'task': 'task3',
            'duration': 5,
        },
        {
            'task': 'task1',
            'duration': 2,
        },
        {
            'task': 'task2',
            'duration': 2,
        },
    ]
    assert workplan.project.resources[1].assigned_tasks == [
        {
            'id': 'task3',
            'title': 'The third task (2/2)',
        },
        {
            'id': 'task1',
            'title': 'The first task',
        },
        {
            'id': 'task2',
            'title': 'The second task (2/2)',
        },
    ]
    assert workplan.project.resources[1].duration == 9
    assert workplan.project.resources[1].end_date == date(2021, 1, 4)
    assert workplan.project.resources[1].use == 100.0
    assert workplan.project.tasks[0].remaining == 0
    assert workplan.project.tasks[1].remaining == 0
    assert workplan.project.tasks[2].remaining == 0
    workplan_dict = workplan.as_dict()
    assert workplan_dict == get_input_file('workplan_complete.yaml')
    str_workplan = yaml_dump(workplan_dict)
    assert str_workplan == get_input_file('workplan_complete.yaml', raw=True)


def test_build_workplan_max_res():
    """Test build_workplan function using max_resources."""
    project = Project(get_input_file('project_complete.yaml'))
    project.tasks[2].max_resources = 1
    workplan = build_workplan(project)
    assert workplan.remaining == 0
    assert workplan.duration == 10
    assert workplan.end_date == date(2021, 1, 5)
    assert workplan.resources_use == 85.0
    assert workplan.project.resources[0].assigned == [
        {
            'task': 'task3',
            'duration': 10,
        },
    ]
    assert workplan.project.resources[0].assigned_tasks == [
        {
            'id': 'task3',
            'title': 'The third task',
        },
    ]
    assert workplan.project.resources[0].duration == 10
    assert workplan.project.resources[0].end_date == date(2021, 1, 5)
    assert workplan.project.resources[0].use == 100.0
    assert workplan.project.resources[1].assigned == [
        {
            'task': 'task2',
            'duration': 5,
        },
        {
            'task': 'task1',
            'duration': 2,
        },
    ]
    assert workplan.project.resources[1].assigned_tasks == [
        {
            'id': 'task2',
            'title': 'The second task',
        },
        {
            'id': 'task1',
            'title': 'The first task',
        },
    ]
    assert workplan.project.resources[1].duration == 7
    assert workplan.project.resources[1].end_date == date(2020, 12, 30)
    assert workplan.project.resources[1].use == 70.0
    assert workplan.project.tasks[0].remaining == 0
    assert workplan.project.tasks[1].remaining == 0
    assert workplan.project.tasks[2].remaining == 0
    workplan_dict = workplan.as_dict()
    assert workplan_dict == \
        get_input_file('workplan_complete_max_resources.yaml')
    str_workplan = yaml_dump(workplan_dict)
    assert str_workplan == \
        get_input_file('workplan_complete_max_resources.yaml', raw=True)
