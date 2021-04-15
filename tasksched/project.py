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

"""Task scheduler project."""

from math import ceil
from operator import attrgetter
from typing import Any, Dict, List

import datetime
import holidays  # type: ignore

from tasksched.utils import (
    is_business_day,
    add_business_days,
    string_to_date,
)

__all__ = (
    'Resource',
    'Task',
    'Project',
)


class Resource:  # pylint: disable=too-few-public-methods
    """A resource."""

    def __init__(self, res_id: str, name: str):
        self.res_id: str = str(res_id)
        self.name: str = name

    def __str__(self) -> str:
        return f'Resource {self.res_id} - {self.name}'


class Task:  # pylint: disable=too-few-public-methods
    """A task."""

    # pylint: disable=too-many-arguments
    def __init__(self, task_id: str, title: str, duration: int,
                 priority: int = 0, max_resources: int = 2):
        self.task_id: str = str(task_id)
        self.title: str = title
        self.duration: int = ceil(duration)
        self.priority: int = priority
        self.max_resources: int = max_resources

    def __str__(self) -> str:
        return (f'Task {self.task_id} - {self.title}: '
                f'{self.duration}d, '
                f'priority: {self.priority}, '
                f'max resources: {self.max_resources}')


class Project:
    """A project."""

    def __init__(self, config: Dict[str, Any]):
        project = config['project']
        self.name: str = project['name']
        self.start_date: datetime.date = string_to_date(project.get('start'))
        self.holidays_iso: str = project.get('holidays')
        if self.holidays_iso:
            self.hdays: Dict = holidays.CountryHoliday(
                self.holidays_iso,
                years=range(self.start_date.year,
                            self.start_date.year + 10),
            )
        else:
            self.hdays = {}
        # adjust the start date to the next business if needed
        if not is_business_day(self.start_date, self.hdays):
            self.start_date = add_business_days(self.start_date, 1, self.hdays)
        self.resources: List[Resource] = [
            Resource(
                res['id'],
                res.get('name', res['id']),
            )
            for res in config['resources']
        ]
        if not self.resources:
            raise ValueError('At least one resource is required')
        self.tasks: List[Task] = [
            Task(
                task['id'],
                task.get('title', task['id']),
                task['duration'],
                task.get('priority', 0),
                task.get('max_resources', 2),
            )
            for task in config['tasks']
            if task['duration'] > 0
        ]
        if not self.tasks:
            raise ValueError('At least one task is required')

    def sorted_tasks(self, key: List[str],
                     reverse: bool = False) -> List[Task]:
        """
        Get list of tasks sorted by priority (from higher to lower) and
        duration (from longest to shortest).

        :param key: key(s) to sort tasks
        :param reverse: reverse sort
        :return: sorted list of tasks
        """
        return sorted(
            self.tasks,
            key=attrgetter(*key),
            reverse=reverse,
        )

    def __str__(self) -> str:
        str_res = '\n'.join([f'    {str(res)}' for res in self.resources])
        str_tasks = '\n'.join([f'    {str(task)}' for task in self.tasks])
        return f"""\
Project: {self.name}
  Resources:
{str_res}
  Tasks:
{str_tasks}
"""
