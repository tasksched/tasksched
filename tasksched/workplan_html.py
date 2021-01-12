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

"""Export work plan to HTML."""

from itertools import cycle

import calendar
import datetime
import os

from jinja2 import Environment, FileSystemLoader

from tasksched.utils import (
    add_business_days,
    get_days,
    get_months,
    string_to_date,
)

__all__ = (
    'workplan_to_html',
)

COLORS = range(10)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')


def get_use_rating(pct):
    """
    Return the use rating for a percentage:
    - 100%: perfect
    - ≥ 80%: good
    - < 80%: bad

    :param int pct: percentage
    :rtype: str
    :return: use rating
    """
    if pct == 100:
        return 'perfect'
    if pct >= 80:
        return 'good'
    return 'bad'


def get_css_tasks():
    """
    Return CSS for tasks.

    :rtype: str
    :return: CSS for tasks
    """
    css_tasks = []
    for i in COLORS:
        css_tasks.append(f"""
.task_color_{i + 1} {{
  background: var(--task-color-{i + 1});
}}""")
    return '\n'.join(css_tasks)


def fill_resources(resources, project_start, tasks_colors, view_days, hdays):
    """
    Fill resources in the workplan with extra data, used by HTML template.

    :param list resources: resources
    :param datetime.date project_start: start date
    :param list tasks_colors: colors for tasks
    :param dict view_days: days
    :param dict hdays: holidays
    """
    for resource in resources:
        tasks_by_id = {}
        for assigned_task in resource['assigned_tasks']:
            tasks_by_id[assigned_task['id']] = {
                'id': assigned_task['id'],
                'title': assigned_task['title'],
                'color': tasks_colors[assigned_task['id']],
            }
        view_assigned = {day: None for day in view_days}
        current_date = project_start
        for task in resource['assigned']:
            count = task['duration']
            if not view_days[current_date]['business_day']:
                current_date = add_business_days(current_date, 1, hdays)
            while count > 0:
                business_day = view_days[current_date]['business_day']
                view_assigned[current_date] = {
                    'task': tasks_by_id[task['task']],
                    'last_day': business_day and count == 1,
                }
                if business_day:
                    count -= 1
                current_date += datetime.timedelta(days=1)
        resource['view_assigned'] = view_assigned
        resource['use_rating'] = get_use_rating(resource['use'])


def workplan_to_html(workplan, template_file='basic', css_file='dark'):
    """
    Export work plan to HTML.

    :param dict workplan: work plan
    :param str template: template name or path to HTML template file (jinja2)
    :param str css: theme (light/dark) or path to CSS file
    :rtype: str
    :return: work plan as HTML
    """
    # pylint: disable=too-many-locals
    project = workplan['workplan']['project']
    resources = workplan['workplan']['resources']
    tasks = workplan['workplan']['tasks']
    project['resources_use_rating'] = get_use_rating(project['resources_use'])
    iter_color = cycle(COLORS)
    tasks_colors = {}
    for task in tasks:
        color = tasks_colors.get(task['id'])
        if color is None:
            color = next(iter_color) + 1
        task['color'] = color
        tasks_colors[task['id']] = color
    project_start = string_to_date(project['start'])
    project_end = string_to_date(project['end'])
    hdays = {
        string_to_date(hday): None
        for hday in project['holidays']
    }
    view_start = project_start.replace(day=1)
    view_end = project_end.replace(
        day=calendar.monthrange(project_end.year, project_end.month)[1])
    view_days = get_days(view_start, view_end, hdays)
    view_months = get_months(view_days)
    days = get_days(project_start, project_end)
    if not template_file.endswith('.html'):
        template_file = os.path.join(DATA_DIR, 'html', f'{template_file}.html')
    if not css_file.endswith('.css'):
        css_file = os.path.join(DATA_DIR, 'css', f'{css_file}.css')
    with open(css_file) as _file:
        css = _file.read().strip()
    css_tasks = get_css_tasks()
    css_months = []
    index = 3
    for i, month in enumerate(view_months):
        css_months.append(f"""
.month{i + 1} {{
  grid-column: {index} / span {month[1]};
}}""")
        index += month[1]
    css_months = '\n'.join(css_months)
    css = f"""
:root {{
  --plan-days: {len(view_days)};
  --plan-resources: {len(resources)};
}}
{css_tasks}
{css_months}
{css}
"""
    fill_resources(resources, project_start, tasks_colors, view_days, hdays)

    # build HTML
    template_dir, filename = os.path.split(os.path.abspath(template_file))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(filename)
    result = template.render(workplan['workplan'], css=css, days=days,
                             view_start=view_start, view_end=view_end,
                             view_days=view_days, view_months=view_months,
                             holidays=project['holidays'])
    return result
