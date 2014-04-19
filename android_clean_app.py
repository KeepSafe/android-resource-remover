"""
    clean_app
    ~~~~~~~~~~

    Implements methods for removing unused android resources based on Android
    Lint results.

    :copyright: (c) 2014 by KeepSafe.
    :license: Apache, see LICENSE for more details.
"""

import argparse
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from lxml import etree


class Issue:

    """
    Stores a single issue reported by Android Lint
    """
    pattern = re.compile('The resource (.+) appears to be unused')

    def __init__(self, filepath, remove_file):
        self.filepath = filepath
        self.remove_file = remove_file
        self.elements = []

    def __str__(self):
        return '{0} {1}'.format(self.filepath)

    def __repr__(self):
        return '{0} {1}'.format(self.filepath)

    def add_element(self, message):
        res = re.findall(Issue.pattern, message)[0]
        bits = res.split('.')[-2:]
        self.elements.append((bits[0], bits[1]))


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--lint',
                        help='Path to the ADT lint tool. If not specified it assumes lint tool is in your path',
                        default='lint')
    parser.add_argument('--app',
                        help='Path to the Android app. If not specifies it assumes current directory is your Android '
                             'app directory',
                        default='.')
    parser.add_argument('--xml',
                        help='Path to the list result. If not specifies linting will be done by the script',
                        default=None)
    parser.add_argument('--ignore-layouts',
                        help='Should ignore layouts',
                        action='store_true')
    args = parser.parse_args()
    print(args)
    return args.lint, args.app, args.xml, args.ignore_layouts


def run_lint_command():
    """
    Run lint command in the shell and save results to lint-result.xml
    """
    lint, app_dir, lint_result, ignore_layouts = parse_args()
    if not lint_result:
        lint_result = os.path.join(app_dir, 'lint-result.xml')
        call_result = subprocess.call([lint, app_dir, '--xml', lint_result], shell=True)
        if call_result > 0:
            print('Running the command failed. Try running it from the console. Arguments for subprocess.call: {0}'.format(
                [lint, app_dir, '--xml', lint_result]))
    return lint_result, app_dir, ignore_layouts


def parse_lint_result(lint_result_path):
    """
    Parse lint-result.xml and create Issue for every problem found
    """
    root = ET.parse(lint_result_path).getroot()
    issues = []
    for issue_xml in root.findall('.//issue[@id="UnusedResources"]'):
        for location in issue_xml.findall('location'):
            filepath = location.get('file')
            # if the location contains line and/or column attribute not the entire resource is unused. that's a guess ;)
            # TODO stop guessing
            remove_entire_file = (location.get('line') or location.get('column')) is None
            issue = Issue(filepath, remove_entire_file)
            issue.add_element(issue_xml.get('message'))
            issues.append(issue)
    return issues


def remove_resource_file(issue, filepath, ignore_layouts):
    """
    Delete a file from the filesystem
    """
    if ignore_layouts is False or issue.elements[0][0] != 'layout':
        print('removing resource: {0}'.format(filepath))
        os.remove(os.path.abspath(filepath))


def remove_resource_value(issue, filepath):
    """
    Read an xml file and remove an element which is unused, then save the file back to the filesystem
    """
    for element in issue.elements:
        print('removing {0} from resource {1}'.format(element, filepath))
        parser = etree.XMLParser(remove_blank_text=False, remove_comments=False, remove_pis=False, strip_cdata=False, resolve_entities=False)
        tree = etree.parse(filepath, parser)
        root = tree.getroot()
        for unused_value in root.findall('.//{0}[@name="{1}"]'.format(element[0], element[1])):
            root.remove(unused_value)
        with open(filepath, 'w') as resource:
            tree.write(resource, encoding='utf-8', xml_declaration=True)


def remove_unused_resources(issues, app_dir, ignore_layouts):
    """
    Remove the file or the value inside the file depending if the whole file is unused or not.
    """
    for issue in issues:
        filepath = os.path.join(app_dir, issue.filepath)
        if issue.remove_file:
            remove_resource_file(issue, filepath, ignore_layouts)
        else:
            remove_resource_value(issue, filepath)


def main():
    lint_result_path, app_dir, ignore_layouts = run_lint_command()
    issues = parse_lint_result(lint_result_path)
    remove_unused_resources(issues, app_dir, ignore_layouts)


if __name__ == '__main__':
    main()
