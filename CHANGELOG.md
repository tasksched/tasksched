<!--
SPDX-FileCopyrightText: 2020-2025 Sébastien Helleu <flashcode@flashtux.org>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Tasksched ChangeLog

## Version 0.5.0 (2021-09-12)

### Changed

- Enable autoescape in Jinja2
- Add type hints in Python code, call mypy static type checker in CI

### Added

- Add information on tasks in HTML output
- Display project name and number of resources in text workplan output
- Add text workplan option `-q`/`--quiet`
- Add lint with bandit
- Add shortcut actions `workplan_text` and `workplan_html`

## Version 0.4.0 (2021-01-23)

### Changed

- **Breaking**: allow YAML files in input, return work plan in YAML by default
- Accept task duration as float in input, round it to the next largest integer
- Ignore tasks with null or negative duration

### Added

- Add workplan option `-j`/`--json`
- Add HTML output with dark (default) and light CSS

### Fixed

- Add missing dependency on `holidays` in setup.py
- Fix traceback displayed when no work plan is received in input with actions text/html

## Version 0.3.0 (2020-11-29)

### Changed

- Adjust the project start date to the next business day if it's a week-end or a public holiday
- Merge resources and tasks from multiple JSON input files when they have the same `id`
- Make resource `name` and task `title` optional fields (use `id` by default)

### Added

- Add task fields `priority` and `max_resources`

### Fixed

- Fix work plan end date
- Fix typo "usage" -> "use"
- Fix colors when tasks are split

## Version 0.2.0 (2020-11-25)

### Changed

- Convert resource and task id to string

### Added

- Add examples directory

### Fixed

- Fix merge of JSON configuration files
- Fix work plan build error on end date if a resource is not used at all
- Fix read of standard input

## Version 0.1.0 (2020-11-24)

### Added

- First release
