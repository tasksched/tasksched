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

"""Tasksched project tests."""

from datetime import date

import os
import pytest

from tasksched import (
    Project,
    Resource,
    Task,
)
from .utils import get_input_file

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_resource():
    """Test Resource class."""
    with pytest.raises(TypeError):
        Resource()  # pylint: disable=no-value-for-parameter
    res = Resource('id', 'The name')
    assert res.res_id == 'id'
    assert res.name == 'The name'
    assert str(res) == 'Resource id - The name'


def test_task():
    """Test Task class."""
    with pytest.raises(TypeError):
        Task()  # pylint: disable=no-value-for-parameter
    task = Task('id', 'the title', 30, 100, 3)
    assert task.task_id == 'id'
    assert task.title == 'the title'
    assert task.duration == 30
    assert task.priority == 100
    assert task.max_resources == 3
    assert str(task) == ('Task id - the title: 30d, priority: 100, '
                         'max resources: 3')


def test_project():  # pylint: disable=too-many-statements
    """Test Project class."""
    with pytest.raises(TypeError):
        Project()  # pylint: disable=no-value-for-parameter
    with pytest.raises(KeyError):
        project = Project({})
    with pytest.raises(KeyError):
        project = Project({'abc': 'def'})

    # missing resources
    with pytest.raises(ValueError):
        project = Project(get_input_file('project_missing_resources.yaml'))

    # missing tasks
    with pytest.raises(ValueError):
        project = Project(get_input_file('project_missing_tasks.yaml'))

    # minimal project
    project = Project(get_input_file('project_minimal.yaml'))
    assert project.name == 'The name'
    assert project.hdays == {}
    assert project.resources[0].res_id == 'dev1'
    assert project.resources[0].name == 'dev1'
    assert project.tasks[0].task_id == 'task1'
    assert project.tasks[0].title == 'task1'
    assert project.tasks[0].duration == 10
    assert project.tasks[0].priority == 0
    assert project.tasks[0].max_resources == 2

    # project starting Saturday
    project = Project(get_input_file('project_start_saturday.yaml'))
    assert project.start_date == date(2020, 11, 30)

    # complete project
    project = Project(get_input_file('project_complete.yaml'))
    assert project.name == 'The name'
    assert project.start_date == date(2020, 12, 21)
    assert project.holidays_iso == 'FRA'
    assert isinstance(project.hdays, dict)
    assert project.hdays
    assert project.hdays.years == set(range(2020, 2030))
    assert len(project.resources) == 2
    assert project.resources[0].res_id == 'dev1'
    assert project.resources[0].name == 'Developer 1'
    assert project.resources[1].res_id == 'dev2'
    assert project.resources[1].name == 'Developer 2'
    assert len(project.tasks) == 3
    assert project.tasks[0].task_id == 'task1'
    assert project.tasks[0].title == 'The first task'
    assert project.tasks[0].duration == 2
    assert project.tasks[0].priority == 0
    assert project.tasks[0].max_resources == 2
    assert project.tasks[1].task_id == 'task2'
    assert project.tasks[1].title == 'The second task'
    assert project.tasks[1].duration == 5
    assert project.tasks[1].priority == 0
    assert project.tasks[1].max_resources == 2
    assert project.tasks[2].task_id == 'task3'
    assert project.tasks[2].title == 'The third task'
    assert project.tasks[2].duration == 10
    assert project.tasks[2].priority == 0
    assert project.tasks[2].max_resources == 2
    assert str(project) == """\
Project: The name
  Resources:
    Resource dev1 - Developer 1
    Resource dev2 - Developer 2
  Tasks:
    Task task1 - The first task: 2d, priority: 0, max resources: 2
    Task task2 - The second task: 5d, priority: 0, max resources: 2
    Task task3 - The third task: 10d, priority: 0, max resources: 2
"""
    # another complete project
    project = Project(get_input_file('project_complete2.yaml'))
    assert project.name == 'The name'
    # only 3 tasks (the task 4 has duration 0 and is ignored)
    assert len(project.tasks) == 3
    assert project.tasks[0].task_id == 'task1'
    assert project.tasks[0].title == 'The first task'
    assert project.tasks[0].duration == 2
    assert project.tasks[0].priority == 0
    assert project.tasks[0].max_resources == 2
    assert project.tasks[1].task_id == 'task2'
    assert project.tasks[1].title == 'The second task'
    assert project.tasks[1].duration == 5
    assert project.tasks[1].priority == 100
    assert project.tasks[1].max_resources == 2
    assert project.tasks[2].task_id == 'task3'
    assert project.tasks[2].title == 'The third task'
    # 10.5 rounded to 11 days
    assert project.tasks[2].duration == 11
    assert project.tasks[2].priority == 0
    assert project.tasks[2].max_resources == 2


def test_project_sort_tasks():
    """Test sort of tasks in a project."""
    project = Project(get_input_file('project_complete.yaml'))
    sorted_tasks = project.sorted_tasks(['duration'])
    assert sorted_tasks[0].task_id == 'task1'
    assert sorted_tasks[1].task_id == 'task2'
    assert sorted_tasks[2].task_id == 'task3'
    project = Project(get_input_file('project_complete.yaml'))
    sorted_tasks = project.sorted_tasks(['duration'], reverse=True)
    assert sorted_tasks[0].task_id == 'task3'
    assert sorted_tasks[1].task_id == 'task2'
    assert sorted_tasks[2].task_id == 'task1'
    project = Project(get_input_file('project_complete2.yaml'))
    sorted_tasks = project.sorted_tasks(['priority', 'duration'],
                                        reverse=True)
    assert sorted_tasks[0].task_id == 'task2'
    assert sorted_tasks[1].task_id == 'task3'
    assert sorted_tasks[2].task_id == 'task1'
