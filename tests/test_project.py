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

"""Tasksched project tests."""

from datetime import date

import os
import pytest

from .utils import get_json_file

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_resource():
    """Test Resource class."""
    from tasksched import Resource
    with pytest.raises(TypeError):
        Resource()
    res = Resource('id', 'The name')
    assert res.res_id == 'id'
    assert res.name == 'The name'
    assert str(res) == 'Resource id - The name'


def test_task():
    """Test Task class."""
    from tasksched import Task
    with pytest.raises(TypeError):
        Task()
    task = Task('id', 'the title', 30)
    assert task.task_id == 'id'
    assert task.title == 'the title'
    assert task.duration == 30
    assert str(task) == 'Task id - the title: 30d'


def test_project():
    """Test Project class."""
    from tasksched import Project
    with pytest.raises(TypeError):
        Project()
    with pytest.raises(KeyError):
        project = Project({})
    with pytest.raises(KeyError):
        project = Project({'abc': 'def'})

    # missing resource
    with pytest.raises(ValueError):
        project = Project(get_json_file('project_missing_resource.json'))

    # missing task
    with pytest.raises(ValueError):
        project = Project(get_json_file('project_missing_task.json'))

    # minimal project
    project = Project(get_json_file('project_minimal.json'))
    assert project.name == 'The name'
    assert project.start_date == date.today()
    assert project.dict_holidays == {}

    # complete project
    project = Project(get_json_file('project_complete.json'))
    assert project.name == 'The name'
    assert project.start_date == date(2020, 12, 21)
    assert project.holidays_iso == 'FRA'
    assert isinstance(project.dict_holidays, dict)
    assert project.dict_holidays.years == set(range(2020, 2030))
    assert project.dict_holidays
    assert len(project.resources) == 2
    assert project.resources[0].res_id == 'dev1'
    assert project.resources[0].name == 'Developer 1'
    assert project.resources[1].res_id == 'dev2'
    assert project.resources[1].name == 'Developer 2'
    assert project.tasks[0].task_id == 'task1'
    assert project.tasks[0].title == 'The first task'
    assert project.tasks[0].duration == 2
    assert project.tasks[1].task_id == 'task2'
    assert project.tasks[1].title == 'The second task'
    assert project.tasks[1].duration == 5
    assert project.tasks[2].task_id == 'task3'
    assert project.tasks[2].title == 'The third task'
    assert project.tasks[2].duration == 10
    tasks_by_duration = project.tasks_by_duration()
    assert tasks_by_duration[0].task_id == 'task3'
    assert tasks_by_duration[1].task_id == 'task2'
    assert tasks_by_duration[2].task_id == 'task1'
    assert str(project) == """\
Project: The name
  Resources:
    Resource dev1 - Developer 1
    Resource dev2 - Developer 2
  Tasks:
    Task task1 - The first task: 2d
    Task task2 - The second task: 5d
    Task task3 - The third task: 10d
"""
