# Task scheduler with automatic resource leveling

[![PyPI](https://img.shields.io/pypi/v/tasksched.svg)](https://pypi.org/project/tasksched/)
[![Build Status](https://github.com/tasksched/tasksched/workflows/CI/badge.svg)](https://github.com/tasksched/tasksched/actions?query=workflow%3A%22CI%22)

The task scheduler reads one or more JSON configuration files, that includes:

- project general information
- list of resources
- list of tasks.

The output is a work plan, with the tasks automatically assigned to resources
("resource leveling"), as JSON format.

The goal is to find the best possible end date (as soon as possible).

The internal algorithm follows these rules:

- efficient use of resources, if possible 100%, with no overload at all
- long tasks may be carried out in parallel by several people.

## Dependencies

Taskshed requires Python ≥ 3.7 and:

- [python-holidays](https://pypi.org/project/holidays/)

You can install dependencies in a virtual environment with:

```
pip install -r requirements.txt
```

## Usage

### Input

The input data is written in JSON format.
One or more files are accepted, each one overwrites any file previously loaded.

The main keys in the input are:

- `project`: project description
- `resources`: list of resources
- `tasks`: list of tasks

The project keys are:

- `name` (string, required): the project name
- `start` (string, optional): the start date, format:  `YYYY-MM-DD` (default: today)
- `holidays` (string, optional): the country ISO code used to skip holidays in work plan
  (for the list of valid country ISO codes, see:
  [python-holidays](https://pypi.org/project/holidays/))
- `resources` (list, required): the list of resources (see below)
- `tasks` (list, resuired): the list of tasks (see below)

For each resource, the keys are:

- `id` (string, required): the resource id
- `name` (string, required): the resource name

For each task, the keys are:

- `id` (string, required): the task id
- `title` (string, required): the task title
- `duration` (integer, required): the task duration in days
- `priority` (integer, optional): the task priority (default: 0), a higher
  priority uses the task first in the work plan, a negative number makes the
  task less urgent than the others
- `max_resources` (integer, optional): the max number of resources to use for
  this task (default: 2)

Content of files can be read from standard input or filenames are allowed as
command line arguments. Both can be used at same time.

The command `tasksched` allows two actions:

- `workplan`: build an optimized work plan using project/resources/tasks info
  in input; the output is JSON data
- `text`: convert output of `workplan` action (JSON data) to text for display
  in the terminal (colors and unicode chars are used by default but optional).

## Examples

### Standard input and multiple JSON files

You can pipe content of JSON files as `tasksched` input.

The following example uses:

- another program called `extract-tasks` to extract tasks from a ticketing tool
- a project configuration file (`project.json`)
- a resources configuration file (`team.json`)
- an extra-tasks configuration file, these tasks are added to the tasks received
  on standard input (`extra_tasks.json`)

So you can build the work plan and convert it to text for display with this command:

```
$ extract-tasks | tasksched workplan project.json team.json extra_tasks.json | tasksched text
```

### Build of work plan

Example of JSON work plan:

```
$ tasksched workplan examples/project_small.json | jq
{
  "workplan": {
    "project": {
      "name": "The big project",
      "start": "2020-12-01",
      "end": "2020-12-07",
      "duration": 4,
      "holidays": "FRA",
      "resources_usage": 87.5
    },
    "resources": [
      {
        "id": "dev1",
        "name": "Developer 1",
        "assigned": [
          "1",
          "1",
          "1"
        ],
        "assigned_tasks": [
          "1"
        ],
        "duration": 3,
        "end": "2020-12-04",
        "usage": 75
      },
      {
        "id": "dev2",
        "name": "Developer 2",
        "assigned": [
          "1",
          "1",
          "2",
          "2"
        ],
        "assigned_tasks": [
          "1",
          "2"
        ],
        "duration": 4,
        "end": "2020-12-07",
        "usage": 100
      }
    ],
    "tasks": [
      {
        "id": "1",
        "title": "The first feature (1/2)",
        "duration": 3,
        "max_resources": 2
      },
      {
        "id": "1",
        "title": "The first feature (2/2)",
        "duration": 2,
        "max_resources": 2
      },
      {
        "id": "2",
        "title": "The second feature",
        "duration": 2,
        "max_resources": 2
      }
    ]
  }
}
```

### Work plan as text

Example of work plan converted to text for display:

```
$ tasksched workplan examples/project_big.json | tasksched text
Legend:
  Task 1: Mega feature (1/2) (16d, prio: 0, max res: 2)
  Task 1: Mega feature (2/2) (16d, prio: 0, max res: 2)
  Task 2: Very nice feature (3d, prio: 0, max res: 2)
  Task 3: Another feature (1/2) (16d, prio: 0, max res: 2)
  Task 3: Another feature (2/2) (16d, prio: 0, max res: 2)
  Task 4: POC for next version (1/2) (7d, prio: 0, max res: 2)
  Task 4: POC for next version (2/2) (7d, prio: 0, max res: 2)
  Task 5: Small feature (1/2) (3d, prio: 0, max res: 2)
  Task 5: Small feature (2/2) (2d, prio: 0, max res: 2)
  Task 6: The most important feature (2d, prio: 100, max res: 2)
  Task 7: Something completely new (5d, prio: 0, max res: 1)
  Task 8: Internal code refactoring (1/2) (9d, prio: 0, max res: 2)
  Task 8: Internal code refactoring (2/2) (8d, prio: 0, max res: 2)

Work plan: 2020-12-01 to 2021-01-12 (28d), 98.21% resources used

  Developer 1 > 2021-01-12  28d 100% █▊███████████████▊██████▊███  6, 3, 4, 5
  Developer 2 > 2021-01-11  27d  96% ███████████████▊████████▊██   1, 8, 5
  Developer 3 > 2021-01-11  27d  96% ███████████████▊███████▊███   1, 8, 2
  Developer 4 > 2021-01-12  28d 100% ███████████████▊██████▊█████  3, 4, 7
```

Note: if you run it in a terminal you'll see colored tasks and bars.

## Copyright

Copyright © 2020 [Sébastien Helleu](https://github.com/flashcode)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
