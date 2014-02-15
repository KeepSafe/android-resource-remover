"""
    clean_app
    ~~~~~~~~~~

    Implements methods for removing unused android resources based on Angular
    Lint results.

    :copyright: (c) 2014 by KeepSafe.
    :license: Apache, see LICENSE for more details.
"""

import argparse
import os
import re
import subprocess
import xml.etree.ElementTree as ET


class Issue:
    """
    Stores a single issue reported by Android Lint
    """
    pattern = re.compile('The resource (.+) appears to be unused')

    def __init__(self, filepath, remove_entire_file):
        self.filepath, self.remove_entire_file = filepath, remove_entire_file
        self.elements = []

    def __str__(self):
        return '{0} {1}'.format(self.filepath, self.remove_entire_file)

    def __repr__(self):
        return '{0} {1}'.format(self.filepath, self.remove_entire_file)

    def add_element(self, message):
        res = re.findall(Issue.pattern, message)[0]
        bits = res.split('.')[-2:]
        self.elements.append((bits[0], bits[1]))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lint',
                        help='Path to the ADT lint tool. If not specified it assumes lint tool is in your path',
                        default='lint')
    parser.add_argument('--app',
                        help='Path to the Android app. If not specifies it assumes current directory is your Android '
                             'app directory',
                        default='.')
    args = parser.parse_args()
    return args.lint, args.app


def run_lint_command():
    lint, app_dir = parse_args()
    result_file = os.path.join(app_dir, 'lint-result.xml')
    call_result = subprocess.call([lint, app_dir, '--xml', result_file], shell=True)
    if call_result > 0:
        print 'Running the command failed. Try running it from the console. Arguments for subprocess.call: {0}'.format(
            [lint, app_dir, '--xml', result_file])
    return result_file, app_dir


def generate_issue_message(issue, location):
    return 'file: {0} line: {1} column: {2}; {3}'.format(location.get('file'), location.get('line'),
                                                         location.get('column'), issue.get('message'))


def parse_lint_result(lint_result_path):
    root = ET.parse(lint_result_path).getroot()
    issues = []
    for issue_xml in root.findall('.//issue[@id="UnusedResources"]'):
        for location in issue_xml.findall('location'):
            filepath = location.get('file')
            # if the location contains line and/or column attribute not the entire resource is unused. that's a guess ;)
            #TODO stop guessing
            remove_entire_file = (location.get('line') or location.get('column')) is None
            issue = Issue(filepath, remove_entire_file)
            if not remove_entire_file:
                issue.add_element(issue_xml.get('message'))
            issues.append(issue)
    return issues


def remove_resource_file(filepath):
    print 'removing resource: {0}'.format(filepath)
    os.remove(os.path.abspath(filepath))


def remove_resource_value(issue, filepath):
    for element in issue.elements:
        print 'removing {0} from resource {1}'.format(element, filepath)
        tree = ET.parse(filepath)
        root = tree.getroot()
        for unused_value in root.findall('.//{0}[@name="{1}"]'.format(element[0], element[1])):
            root.remove(unused_value)
        with open(filepath, 'w') as resource:
            tree.write(resource, encoding='utf-8', xml_declaration=True)


def remove_unused_resources(issues, app_dir):
    for issue in issues:
        filepath = os.path.join(app_dir, issue.filepath)
        if issue.remove_entire_file:
            remove_resource_file(filepath)
        elif len(issue.elements) > 0:
            remove_resource_value(issue, filepath)


if __name__ == '__main__':
    lint_result_path, app_dir = run_lint_command()
    issues = parse_lint_result(lint_result_path)
    remove_unused_resources(issues, app_dir)

