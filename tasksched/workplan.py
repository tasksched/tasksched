#!/usr/bin/env python3
#
# Copyright (C) 2020-2022 Sébastien Helleu <flashcode@flashtux.org>
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

"""Task scheduler work plan."""

from operator import attrgetter
from typing import Dict, List, Optional

import copy
import datetime

from tasksched.project import Project, Resource, Task
from tasksched.utils import add_business_days

__all__ = (
    "WorkPlan",
    "build_workplan",
)


class WorkPlanResource(Resource):  # pylint: disable=too-few-public-methods
    """A workplan resource."""

    def __init__(self, res_id: str, name: str):
        super().__init__(res_id, name)
        self.assigned: List[Dict] = []
        self.assigned_tasks: List[Dict] = []
        self.duration: int = 0
        self.end_date: Optional[datetime.date] = None
        self.use: int = 0


class WorkPlanTask(Task):  # pylint: disable=too-few-public-methods
    """A workplan task."""

    # pylint: disable=too-many-arguments
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remaining: int = self.duration


class WorkPlan:
    """A work plan built for a project."""

    def __init__(
        self, project: Project, tasks_to_split: Dict[str, int] = None
    ):
        self.project = copy.deepcopy(project)
        self.resources = [
            WorkPlanResource(res.res_id, res.name)
            for res in self.project.resources
        ]
        self.tasks = [
            WorkPlanTask(
                task.task_id,
                task.title,
                task.duration,
                task.priority,
                task.max_resources,
            )
            for task in self.project.tasks
        ]
        if tasks_to_split:
            self.split_tasks(tasks_to_split)
        self.remaining = sum(task.duration for task in self.tasks)
        self.duration = 0
        self.end_date = self.project.start_date
        self.resources_use = 0
        self.schedule()

    def split_tasks(self, tasks_to_split: Dict[str, int]):
        """
        Split tasks in the project, to carry them out in parallel by several
        people.

        :param tasks_to_split: tasks to split, keys are task ids (str),
            values are number of splits (int)
        """
        new_tasks = []
        for task in self.tasks:
            number = tasks_to_split.get(task.task_id, None)
            if number is not None and 1 < number <= task.max_resources:
                # split duration into multiple durations which are all almost
                # the same, and sum == duration (and remove all null values);
                # for example if task.duration == 10 and number == 3,
                # durations == [4, 3, 3]
                durations = list(
                    filter(
                        None,
                        [
                            task.duration // number
                            + (1 if x < task.duration % number else 0)
                            for x in range(number)
                        ],
                    )
                )
                for i, duration in enumerate(durations):
                    title = f"{task.title} ({i+1}/{len(durations)})"
                    new_tasks.append(
                        WorkPlanTask(
                            task.task_id,
                            title,
                            duration,
                            task.priority,
                            task.max_resources,
                        )
                    )
            else:
                new_tasks.append(
                    WorkPlanTask(
                        task.task_id,
                        task.title,
                        task.duration,
                        task.priority,
                        task.max_resources,
                    )
                )
        self.tasks = new_tasks

    def find_best_resource(self) -> Resource:
        """
        Find the best resource to use (the less used resource, by order).

        :return: resource found
        """
        lowest_duration = 999999999
        best_res = None
        for res in self.resources:
            if res.duration == 0:
                return res
            if res.duration < lowest_duration:
                lowest_duration = res.duration
                best_res = res
        return best_res or self.resources[0]

    def assign_task(self, task, resource, days):
        """
        Assign a task to a resource.

        :param Task task: task
        :param Resource resource: resource
        :param int days: number of days in task to assign
        """
        resource.assigned.append(
            {
                "task": task.task_id,
                "duration": days,
            }
        )
        resource.assigned_tasks.append(
            {
                "id": task.task_id,
                "title": task.title,
            }
        )
        resource.duration += days
        if resource.duration > self.duration:
            self.duration = resource.duration
        task.remaining -= days
        self.remaining -= days

    def sorted_tasks(
        self, key: List[str], reverse: bool = False
    ) -> List[Task]:
        """
        Get list of tasks sorted by priority (from higher to lower) and
        duration (from longest to shortest).

        :param tuple,list key: key(s) to sort tasks
        :param bool reverse: reverse sort
        :return: sorted list of tasks
        """
        return sorted(
            self.tasks,
            key=attrgetter(*key),
            reverse=reverse,
        )

    def schedule(self):
        """Automatic resource leveling in the project."""
        sorted_tasks = self.sorted_tasks(
            ["priority", "duration"], reverse=True
        )
        for task in sorted_tasks:
            self.assign_task(task, self.find_best_resource(), task.remaining)
        sum_use = 0
        for res in self.resources:
            if res.duration > 0:
                res.end_date = add_business_days(
                    self.project.start_date,
                    res.duration - 1,
                    self.project.hdays,
                )
                if res.end_date > self.end_date:
                    self.end_date = res.end_date
            res.use = (res.duration * 100) / self.duration
            sum_use += res.use
        if self.resources:
            self.resources_use = sum_use / len(self.resources)

    def as_dict(self) -> Dict:
        """Return the work plan as dict."""
        after_end = self.end_date + datetime.timedelta(days=1)
        holidays = self.project.hdays[
            self.project.start_date : after_end  # type: ignore
        ]
        return {
            "workplan": {
                "project": {
                    "name": self.project.name,
                    "start": self.project.start_date,
                    "end": self.end_date,
                    "duration": self.duration,
                    "holidays_iso": self.project.holidays_iso,
                    "holidays": holidays,
                    "resources_use": self.resources_use,
                },
                "resources": [
                    {
                        "id": res.res_id,
                        "name": res.name,
                        "assigned": res.assigned,
                        "assigned_tasks": res.assigned_tasks,
                        "duration": res.duration,
                        "end": res.end_date or None,
                        "use": res.use,
                    }
                    for res in self.resources
                ],
                "tasks": [
                    {
                        "id": task.task_id,
                        "title": task.title,
                        "duration": task.duration,
                        "priority": task.priority,
                        "max_resources": task.max_resources,
                    }
                    for task in self.tasks
                ],
            },
        }


def build_workplan(project: Project) -> WorkPlan:
    """
    Build a work plan and tries to split tasks for the smallest possible
    project duration.

    :param project: the project
    :return: work plan
    """
    tasks_ids = [
        task.task_id
        for task in project.sorted_tasks(["duration"], reverse=True)
        if task.duration > 1
    ]
    best_workplan = WorkPlan(project)
    for i in range(0, len(tasks_ids)):
        tasks_to_split = {task_id: 2 for task_id in tasks_ids[: i + 1]}
        workplan = WorkPlan(project, tasks_to_split=tasks_to_split)
        if workplan.duration < best_workplan.duration:
            best_workplan = workplan
    return best_workplan
