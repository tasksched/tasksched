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

"""Task scheduler project."""

from operator import attrgetter

import datetime

import holidays

__all__ = (
    'Resource',
    'Task',
    'Project',
)


class Resource:  # pylint: disable=too-few-public-methods
    """A resource."""

    def __init__(self, res_id, name):
        self.res_id = res_id
        self.name = name

    def __str__(self):
        return f'Resource {self.res_id} - {self.name}'


class Task:  # pylint: disable=too-few-public-methods
    """A task."""

    def __init__(self, task_id, title, duration):
        self.task_id = task_id
        self.title = title
        self.duration = duration

    def __str__(self):
        return f'Task {self.task_id} - {self.title}: {self.duration}d'


class Project:
    """A project."""

    def __init__(self, config):
        project = config['project']
        self.name = project['name']
        self.start_date = datetime.date.fromisoformat(
            project.get('start', datetime.date.today().strftime('%Y-%m-%d'))
        )
        self.holidays_iso = project.get('holidays')
        if self.holidays_iso:
            self.dict_holidays = holidays.CountryHoliday(
                self.holidays_iso,
                years=range(self.start_date.year,
                            self.start_date.year + 10),
            )
        else:
            self.dict_holidays = {}
        self.resources = [
            Resource(res['id'], res['name'])
            for res in config['resources']
        ]
        if not self.resources:
            raise ValueError('At least one resource is required')
        self.tasks = [
            Task(task['id'], task['title'], task['duration'])
            for task in config['tasks']
        ]
        if not self.tasks:
            raise ValueError('At least one task is required')

    def tasks_by_duration(self):
        """
        Get list of tasks sorted duration from longest to shortest.

        :rtype: list
        :return: list of tasks with remaining days > 0, sorted by longest to
            shortest
        """
        return sorted(self.tasks, key=attrgetter('duration'), reverse=True)

    def __str__(self):
        str_res = '\n'.join([f'    {str(res)}' for res in self.resources])
        str_tasks = '\n'.join([f'    {str(task)}' for task in self.tasks])
        return f"""\
Project: {self.name}
  Resources:
{str_res}
  Tasks:
{str_tasks}
"""
