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
import distutils.spawn
from lxml import etree

ANDROID_MANIFEST_FILE = 'AndroidManifest.xml'


class Issue:

    """
    Stores a single issue reported by Android Lint
    """

    def __init__(self, filepath, remove_file):
        self.filepath = filepath
        self.remove_file = remove_file
        self.elements = []

    def __str__(self):
        return '{0} {1}'.format(self.filepath, self.elements)

    def __repr__(self):
        return '{0} {1}'.format(self.filepath, self.elements)

    def add_element(self, message):
        res_all = re.findall(self.pattern, message)
        if res_all:
            self._process_match(res_all)
        else:
            print("The pattern '%s' seems to find nothing in the error message '%s'. We can't find the resource and "
                  "can't remove it. The pattern might have changed, please check and report this in github issues." % (
                      self.pattern.pattern, message))


class UnusedResourceIssue(Issue):
    pattern = re.compile('The resource `?([^`]+)`? appears to be unused')

    def _process_match(self, match_result):
        bits = match_result[0].split('.')[-2:]
        self.elements.append((bits[0], bits[1]))


class ExtraTranslationIssue(Issue):
    pattern = re.compile('The resource string \"`([^`]+)`\" has been marked as `translatable=\"false')

    def _process_match(self, match_result):
        self.elements.append(('string', match_result[0]))


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
                        help='Path to the lint result. If not specifies linting will be done by the script',
                        default=None)
    parser.add_argument('--ignore-layouts',
                        help='Should ignore layouts',
                        action='store_true')
    args = parser.parse_args()
    return args.lint, args.app, args.xml, args.ignore_layouts


def run_lint_command():
    """
    Run lint command in the shell and save results to lint-result.xml
    """
    lint, app_dir, lint_result, ignore_layouts = parse_args()
    if not lint_result:
        if not distutils.spawn.find_executable(lint):
            raise Exception(
                '`%s` executable could not be found and path to lint result not specified. See --help' % lint)
        lint_result = os.path.join(app_dir, 'lint-result.xml')
        call_result = subprocess.call([lint, app_dir, '--xml', lint_result])
        if call_result > 0:
            print('Running the command failed with result %s. Try running it from the console.'
                  ' Arguments for subprocess.call: %s' % (call_result, [lint, app_dir, '--xml', lint_result]))
    else:
        if not os.path.isabs(lint_result):
            lint_result = os.path.join(app_dir, lint_result)
    lint_result = os.path.abspath(lint_result)
    return lint_result, app_dir, ignore_layouts


def get_manifest_string_refs(manifest_path):
    pattern = re.compile('="@string/([^"]+)"')
    with open(manifest_path, 'r') as f:
        data = f.read()
        refs = set(re.findall(pattern, data))
        return [x.replace('/', '.') for x in refs]


def _get_issues_from_location(issue_class, locations, message):
    issues = []
    for location in locations:
        filepath = location.get('file')
        # if the location contains line and/or column attribute not the entire resource is unused.
        # that's a guess ;)
        # TODO stop guessing
        remove_entire_file = (location.get('line') or location.get('column')) is None
        issue = issue_class(filepath, remove_entire_file)
        issue.add_element(message)
        issues.append(issue)
    return issues


def parse_lint_result(lint_result_path, manifest_path):
    """
    Parse lint-result.xml and create Issue for every problem found except unused strings referenced in AndroidManifest
    """
    unused_string_pattern = re.compile('The resource `R\.string\.([^`]+)` appears to be unused')
    mainfest_string_refs = get_manifest_string_refs(manifest_path)
    root = etree.parse(lint_result_path).getroot()
    issues = []

    for issue_xml in root.findall('.//issue[@id="UnusedResources"]'):
        message = issue_xml.get('message')
        unused_string = re.match(unused_string_pattern, issue_xml.get('message'))
        has_string_in_manifest = unused_string and unused_string.group(1) in mainfest_string_refs
        if not has_string_in_manifest:
            issues.extend(_get_issues_from_location(UnusedResourceIssue,
                                                    issue_xml.findall('location'),
                                                    message))

    for issue_xml in root.findall('.//issue[@id="ExtraTranslation"]'):
        message = issue_xml.get('message')
        if re.findall(ExtraTranslationIssue.pattern, message):
            issues.extend(_get_issues_from_location(ExtraTranslationIssue,
                                                    issue_xml.findall('location'),
                                                    message))

    return issues


def remove_resource_file(issue, filepath, ignore_layouts):
    """
    Delete a file from the filesystem
    """
    if os.path.exists(filepath) and (ignore_layouts is False or issue.elements[0][0] != 'layout'):
        print('removing resource: {0}'.format(filepath))
        os.remove(os.path.abspath(filepath))


def remove_resource_value(issue, filepath):
    """
    Read an xml file and remove an element which is unused, then save the file back to the filesystem
    """
    if os.path.exists(filepath):
        for element in issue.elements:
            print('removing {0} from resource {1}'.format(element, filepath))
            parser = etree.XMLParser(remove_blank_text=False, remove_comments=False,
                                     remove_pis=False, strip_cdata=False, resolve_entities=False)
            tree = etree.parse(filepath, parser)
            root = tree.getroot()
            for unused_value in root.findall('.//{0}[@name="{1}"]'.format(element[0], element[1])):
                root.remove(unused_value)
            with open(filepath, 'wb') as resource:
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
    if os.path.exists(lint_result_path):
        manifest_path = os.path.abspath(os.path.join(app_dir, ANDROID_MANIFEST_FILE))
        issues = parse_lint_result(lint_result_path, manifest_path)
        remove_unused_resources(issues, app_dir, ignore_layouts)
    else:
        print('the file with lint results could not be found: %s' % lint_result_path)


if __name__ == '__main__':
    main()
