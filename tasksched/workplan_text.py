#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2020-2025 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

"""Export work plan to text."""

from itertools import cycle
from typing import Dict

__all__ = (
    "workplan_to_text",
)

COLORS = (1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 27, 174, 165, 75)


def color(text: str, color_code: int) -> str:
    """Return a colored text with ANSI color code."""
    return f"\033[38;5;{color_code}m{text}"


def color_pct(text: str, pct: int) -> str:
    """
    Return the color for a percentage display:
    - 100%: green (10)
    - ≥ 80%: orange (214)
    - < 80%: red (9)

    :param text: the text to display
    :param pct: percentage
    :return: colored percentage with color reset after
    """
    if pct == 100:
        color_code = 10  # green (perfect use)
    elif pct >= 80:
        color_code = 214  # orange (good use)
    else:
        color_code = 9  # red (not used enough)
    pct_color = color(text, color_code)
    return f"{pct_color}\033[0m"


def workplan_to_text(  # pylint: disable=too-many-locals
    workplan: Dict,
    quiet: bool = False,
    use_colors: bool = True,
    use_unicode: bool = True,
) -> str:
    """
    Export work plan to text.

    :param workplan: work plan
    :param quiet: display work plan summary (no legend/tasks)
    :param use_colors: use ANSI colors in output
    :param use_unicode: use unciode chars in output
    :return: work plan as string
    """
    color_reset = "\033[0m" if use_colors else ""
    project = workplan["workplan"]["project"]
    resources = workplan["workplan"]["resources"]
    resources_count = len(resources)
    tasks = workplan["workplan"]["tasks"]
    legend = ["Legend:"]
    iter_color = cycle(COLORS)
    tasks_colors = {}
    for task in tasks:
        if task["id"] not in tasks_colors:
            tasks_colors[task["id"]] = next(iter_color)
        str_id = (
            color(task["id"], tasks_colors[task["id"]])
            if use_colors
            else task["id"]
        )
        legend.append(
            f'  Task {str_id}: {task["title"]}{color_reset} '
            f'({task["duration"]}d, prio: {task["priority"]}, '
            f'max res: {task["max_resources"]})'
        )
    text = f'{project["resources_use"]:.2f}%'
    res_use = (
        color_pct(text, project["resources_use"]) if use_colors else text
    )
    info = (
        f'{project["name"]}: {project["start"]} to {project["end"]} '
        f'({project["duration"]}d), {res_use} of {resources_count} '
        f"resources used"
    )
    rows = [""]
    max_len_res = (
        max(len(res["name"]) for res in resources) + 2 if resources else 0
    )
    if use_unicode:
        bar_chars = ["█", "█", "▊"]
    else:
        bar_chars = ["[", "x", "]"]
    for res in resources:
        text = f'{res["use"]:>3.0f}%'
        use = color_pct(text, res["use"]) if use_colors else text
        chars = []
        for task in res["assigned"]:
            chars_task = [bar_chars[1]] * task["duration"]
            chars_task[0] = bar_chars[0]
            chars_task[-1] = bar_chars[2]
            str_task = "".join(chars_task)
            chars.append(
                color(str_task, tasks_colors[task["task"]])
                if use_colors
                else str_task
            )
        bar_resource = "".join(chars)
        tasks = ", ".join([task["id"] for task in res["assigned_tasks"]])
        filler = " " * (project["duration"] - res["duration"] + 2)
        rows.append(
            f'{res["name"]:>{max_len_res}} > {res["end"] or " "*10} '
            f'{res["duration"]:>3}d {use} '
            f"{bar_resource}{color_reset}{filler}{tasks}"
        )
    if quiet:
        return info
    return "\n".join(
        [
            "\n".join(legend),
            "",
            info,
            "\n".join(rows),
        ]
    )
