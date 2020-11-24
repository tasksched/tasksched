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

"""Tasksched work plan tests."""

from datetime import date

import pytest

from .utils import get_json_file


def test_workplan():
    """Test WorkPlan class."""
    from tasksched import Project, WorkPlan
    with pytest.raises(TypeError):
        WorkPlan()
    project = Project(get_json_file('project_complete.json'))
    workplan = WorkPlan(project)
    assert workplan.remaining == 0
    assert workplan.duration == 10
    assert workplan.end_date == date(2021, 1, 6)
    assert workplan.resources_usage == 85.0
    assert workplan.project.resources[0].assigned == ['task3'] * 10
    assert workplan.project.resources[0].assigned_tasks == ['task3']
    assert workplan.project.resources[0].duration == 10
    assert workplan.project.resources[0].end_date == date(2021, 1, 6)
    assert workplan.project.resources[0].usage == 100
    assert workplan.project.resources[1].assigned == (
        (['task2'] * 5) + (['task1'] * 2)
    )
    assert workplan.project.resources[1].assigned_tasks == ['task2', 'task1']
    assert workplan.project.resources[1].duration == 7
    assert workplan.project.resources[1].end_date == date(2020, 12, 31)
    assert workplan.project.resources[1].usage == 70
    assert workplan.project.tasks[0].remaining == 0
    assert workplan.project.tasks[1].remaining == 0
    assert workplan.project.tasks[2].remaining == 0


def test_workplan_split_2():
    """Test WorkPlan class with split of tasks into 2."""
    from tasksched import Project, WorkPlan
    workplan = WorkPlan(Project(get_json_file('project_complete.json')),
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
    from tasksched import Project, WorkPlan
    workplan = WorkPlan(Project(get_json_file('project_complete.json')),
                        {'task2': 3})
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
    """Test build of work plan."""
    from tasksched import Project, build_workplan
    workplan = build_workplan(Project(get_json_file('project_complete.json')))
    assert workplan.remaining == 0
    assert workplan.duration == 9
    assert workplan.end_date == date(2021, 1, 5)
    assert workplan.resources_usage == 94.44444444444444
    assert workplan.project.resources[0].assigned == (
        (['task3'] * 5) + (['task2'] * 3)
    )
    assert workplan.project.resources[0].assigned_tasks == [
        'task3', 'task2',
    ]
    assert workplan.project.resources[0].duration == 8
    assert workplan.project.resources[0].end_date == date(2021, 1, 4)
    assert workplan.project.resources[0].usage == 88.88888888888889
    assert workplan.project.resources[1].assigned == (
        (['task3'] * 5) + (['task1'] * 2) + (['task2'] * 2)
    )
    assert workplan.project.resources[1].assigned_tasks == [
        'task3', 'task1', 'task2',
    ]
    assert workplan.project.resources[1].duration == 9
    assert workplan.project.resources[1].end_date == date(2021, 1, 5)
    assert workplan.project.resources[1].usage == 100.0
    assert workplan.project.tasks[0].remaining == 0
    assert workplan.project.tasks[1].remaining == 0
    assert workplan.project.tasks[2].remaining == 0
    assert workplan.as_dict() == get_json_file('workplan_complete.json')
