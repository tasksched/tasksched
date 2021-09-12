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

"""Task scheduler with automatic resource leveling."""

from typing import Any, Dict, IO, List, Union

import json
import sys

import yaml

from tasksched.parser import get_parser
from tasksched.project import Project
from tasksched.workplan import build_workplan
from tasksched.workplan_text import workplan_to_text
from tasksched.workplan_html import workplan_to_html
from tasksched.utils import yaml_dump

__version__ = '0.6.0-dev'

__all__ = (
    '__version__',
    'load_config',
    'main',
    'init',
)


def error(message: str):
    """
    Display an error.

    :param message: error message to display
    """
    print(message, file=sys.stderr)
    print('Try with --help to get help on tasksched', file=sys.stderr)


def get_input_files(args) -> List[Any]:
    """
    Get list of input files (optional stdin file + filenames).

    :param argparse.Namespace args: command-line arguments
    :return: list of files/filenames
    """
    files = []
    if not sys.stdin.isatty():
        files.append(sys.stdin)
    files.extend(args.filename)
    return files


def read_file(input_file: Union[IO, str]) -> Dict:
    """
    Read input file (YAML or JSON).

    :param input_file: input file
    :return: input file as dict
    """
    try:
        if isinstance(input_file, str):
            with open(input_file) as _file:
                return yaml.safe_load(_file)
        else:
            return yaml.safe_load(input_file)
    except (FileNotFoundError, yaml.parser.ParserError) as exc:
        if isinstance(input_file, str):
            error(f'ERROR: unable to decode input file "{input_file}": {exc}')
        else:
            error(f'ERROR: unable to decode input data: {exc}')
        raise


def search_item(list_items: List[Any], item_id: Any) -> Any:
    """
    Search an item by its id in a list.

    :param list_items: list of items
    :param item_id: item id to search in the list of items
    :return: the item found or None
    """
    if item_id:
        for item in list_items:
            if item['id'] == item_id:
                return item
    return None


def merge_configs(config: Dict, new_config: Dict):
    """
    Merge config2 into config: each value in config is updated with value
    from config2: for dicts (like "project"), keys are updated, for lists
    (like "resources" or "tasks"), items are added to the list.

    :param dict config: first config to update
    :param dict new_config: dictionary used to update the config
    """
    for key, value in new_config.items():
        if key not in config:
            config[key] = value
            continue
        if isinstance(config[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f'merge config error: '
                                 f'cannot update dict "{key}"')
            config[key].update(value)
        elif isinstance(config[key], list):
            if not isinstance(value, list):
                raise ValueError(f'merge config error: '
                                 f'cannot update list "{key}"')
            for item in value:
                if isinstance(item, dict):
                    config_item = search_item(config[key], item.get('id'))
                    if config_item is None:
                        config[key].append(item)
                    else:
                        config_item.update(item)
                else:
                    config[key].append(item)
        else:
            config[key] = value


def load_config(files: List[Any]) -> Dict:
    """
    Load YAML/JSON configuration by reading stdin (if available) and list of
    input files received on command line.

    :param list files: files/filenames to load
    :return: configuration
    """
    config: Dict[Any, Any] = {}
    for _file in files:
        new_config = read_file(_file)
        if new_config:
            merge_configs(config, new_config)
    return config


def load_project(args) -> Project:
    """
    Load project.

    :param argparse.Namespace args: command-line arguments
    :return: project
    """
    files = get_input_files(args)
    config = load_config(files)
    try:
        return Project(config)
    except (KeyError, ValueError) as exc:
        error(f'ERROR: invalid project: "{exc.args[0]}"')
        raise


def read_workplan(args) -> Dict:
    """
    Read work plan.

    :param argparse.Namespace args: command-line arguments
    :return: work plan as dict
    """
    workplan = None
    files = get_input_files(args)
    if files:
        workplan = read_file(files[-1])
    if not workplan:
        error('ERROR: missing input work plan')
        raise OSError('missing input work plan')
    return workplan


def convert_workplan_to_text(workplan: Dict, args) -> str:
    """
    Convert workplan to text.

    :param workplan: work plan
    :param argparse.Namespace args: command-line arguments
    """
    try:
        return workplan_to_text(
            workplan,
            quiet=args.quiet,
            use_colors=not args.no_colors,
            use_unicode=not args.no_unicode,
        )
    except (KeyError, ValueError) as exc:
        error(f'ERROR: invalid work plan: "{exc}"')
        raise


def convert_workplan_to_html(workplan: Dict, args) -> str:
    """
    Convert workplan to HTML.

    :param workplan: work plan
    :param argparse.Namespace args: command-line arguments
    """
    try:
        return workplan_to_html(
            workplan,
            template_file=args.template,
            css_file=args.css,
        )
    except (KeyError, ValueError) as exc:
        error(f'ERROR: invalid work plan: "{exc}"')
        raise


def action_workplan(args):
    """
    Return the work plan using the project configuration.

    :param argparse.Namespace args: command-line arguments
    """
    project = load_project(args)
    workplan = build_workplan(project)
    if args.json:
        return json.dumps(workplan.as_dict(), default=str)
    return yaml_dump(workplan.as_dict())


def action_text(args):
    """
    Return the work plan as text to display in the terminal.

    :param argparse.Namespace args: command-line arguments
    """
    workplan = read_workplan(args)
    return convert_workplan_to_text(workplan, args)


def action_html(args):
    """
    Return the work plan as HTML.

    :param argparse.Namespace args: command-line arguments
    """
    workplan = read_workplan(args)
    return convert_workplan_to_html(workplan, args)


def action_workplan_text(args):
    """
    Build the work plan and return it as text to display in the terminal.

    :param argparse.Namespace args: command-line arguments
    """
    project = load_project(args)
    workplan = build_workplan(project)
    return convert_workplan_to_text(workplan.as_dict(), args)


def action_workplan_html(args):
    """
    Build the work plan and return it as HTML.

    :param argparse.Namespace args: command-line arguments
    """
    project = load_project(args)
    workplan = build_workplan(project)
    return convert_workplan_to_html(workplan.as_dict(), args)


def main():
    """Main function, entry point."""
    args = get_parser(__version__).parse_args()
    func = getattr(sys.modules[__name__], f'action_{args.action}')
    try:
        result = func(args)
    except Exception:  # pylint: disable=broad-except
        sys.exit(1)
    print(result)


def init(force=False):
    """Init function."""
    if __name__ == '__main__' or force:
        main()


init()
