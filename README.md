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

Taskshed requires Python ≥ 3.6 and:

- [python-holidays](https://pypi.org/project/holidays/)

You can install dependencies in a virtual environment with:

```
pip install -r requirements.txt
```

## Usage

The input data is written in JSON format.
One or more files are accepted, each one overwrites any file previously loaded.

Content of files can be read from standard input or filenames are allowed as
command line arguments. Both can be used at same time.

The command `tasksched` allows two actions:

- `workplan`: build an optimized work plan using project/resources/tasks info
  in input; the output is JSON data
- `text`: convert output of `workplan` action (JSON data) to text for display
  in the terminal (colors and unicode chars are used by default but optional).

See file [project_complete.json](tests/project_complete.json) for an example
of input JSON files with all possible fields and file
[workplan_complete.json](tests/workplan_complete.json) for an example of output
workplan, as JSON.

Example: use of another program `extract-tasks` to extract tasks from a ticketing
tool and two configuration files for the project and resources, build the work plan
and convert it to text for display:

```
$ extract-tasks | tasksched workplan project.json team.json | tasksched text
```

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
