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

import json
import sys

import yaml

from tasksched.parser import get_parser
from tasksched.project import Project
from tasksched.workplan import build_workplan
from tasksched.workplan_text import workplan_to_text
from tasksched.workplan_html import workplan_to_html
from tasksched.utils import yaml_dump

__version__ = '0.4.0'

__all__ = (
    '__version__',
    'load_config',
    'main',
    'init',
)


def fatal(error):
    """
    Display a fatal error and exit with return code 1.

    :param str error: error to display
    """
    print(error, file=sys.stderr)
    print('Try with --help to get help on tasksched', file=sys.stderr)
    sys.exit(1)


def get_input_files(args):
    """
    Get list of input files (optional stdin file + filenames).

    :rtype: list
    :return: list of files/filenames
    """
    files = []
    if not sys.stdin.isatty():
        files.append(sys.stdin)
    files.extend(args.filename)
    return files


def read_file(input_file):
    """
    Read input file (YAML or JSON).

    :param object,str input_file: input file
    :rtype: dict
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
            fatal(f'ERROR: unable to decode input file "{input_file}": {exc}')
        else:
            fatal(f'ERROR: unable to decode input data: {exc}')


def search_item(list_items, item_id):
    """
    Search an item by its id in a list.

    :param list list_items: list of items
    :param str item_id: item id to search in the list of items
    :rtype: object
    :return: the item found or None
    """
    if item_id:
        for item in list_items:
            if item['id'] == item_id:
                return item
    return None


def merge_configs(config, new_config):
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


def load_config(files):
    """
    Load YAML/JSON configuration by reading stdin (if available) and list of
    input files received on command line.

    :param list files: files/filenames to load
    :rtype: dict
    :return: configuration
    """
    config = {}
    for _file in files:
        new_config = read_file(_file)
        if new_config:
            merge_configs(config, new_config)
    return config


def action_workplan(args):
    """
    Return the work plan using the project configuration.

    :param argparse.Namespace args: command-line arguments
    """
    files = get_input_files(args)
    config = load_config(files)
    try:
        project = Project(config)
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid project: "{exc.args[0]}"')
    workplan = build_workplan(project)
    if args.json:
        return json.dumps(workplan.as_dict(), default=str)
    return yaml_dump(workplan.as_dict())


def read_workplan(args):
    """
    Read work plan.

    :param argparse.Namespace args: command-line arguments
    :rtype: dict
    :return: work plan as dict
    """
    workplan = None
    files = get_input_files(args)
    if files:
        workplan = read_file(files[-1])
    if not workplan:
        fatal('ERROR: missing input workplan')
    return workplan


def action_text(args):
    """
    Return the work plan as text to display in the terminal.

    :param argparse.Namespace args: command-line arguments
    """
    config = read_workplan(args)
    try:
        return workplan_to_text(
            config,
            use_colors=not args.no_colors,
            use_unicode=not args.no_unicode,
        )
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid work plan: "{exc}"')


def action_html(args):
    """
    Return the work plan as HTML.

    :param argparse.Namespace args: command-line arguments
    """
    config = read_workplan(args)
    try:
        return workplan_to_html(
            config,
            template_file=args.template,
            css_file=args.css,
        )
    except (KeyError, ValueError) as exc:
        fatal(f'ERROR: invalid work plan: "{exc}"')


def main():
    """Main function, entry point."""
    args = get_parser(__version__).parse_args()
    func = getattr(sys.modules[__name__], f'action_{args.action}')
    result = func(args)
    print(result)


def init(force=False):
    """Init function."""
    if __name__ == '__main__' or force:
        main()


init()
