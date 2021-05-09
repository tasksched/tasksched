# Tasksched ChangeLog

## Version 0.5.0 (under dev)

- Add shortcut actions `workplan_text` and `workplan_html`.
- Add type hints in Python code, call mypy static type checker in CI.

## Version 0.4.0 (2021-01-23)

- Allow YAML files in input, return work plan in YAML by default.
- Add workplan option `-j`/`--json`.
- Add HTML output with dark (default) and light CSS.
- Accept task duration as float in input, round it to the next largest integer.
- Ignore tasks with null or negative duration.
- Add missing dependency on `holidays` in setup.py.
- Fix traceback displayed when no work plan is received in input with actions text/html.

## Version 0.3.0 (2020-11-29)

- Adjust the project start date to the next business day if it's a week-end or a public holiday.
- Fix work plan end date.
- Fix typo "usage" -> "use".
- Fix colors when tasks are split.
- Merge resources and tasks from multiple JSON input files when they have the same `id`.
- Make resource `name` and task `title` optional fields (use `id` by default).
- Add task fields `priority` and `max_resources`.

## Version 0.2.0 (2020-11-25)

- Add examples directory.
- Fix merge of JSON configuration files.
- Fix work plan build error on end date if a resource is not used at all.
- Fix read of standard input.
- Convert resource and task id to string.

## Version 0.1.0 (2020-11-24)

- First release.
