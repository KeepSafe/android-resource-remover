import argparse
import os
import subprocess
import xml.etree.ElementTree as ET


class Issue:
    def __init__(self, filepath, safe_remove):
        self.filepath, self.safe_remove = filepath, safe_remove

    def __str__(self):
        return '{0} {1}'.format(self.filepath, self.safe_remove)

    def __repr__(self):
        return '{0} {1}'.format(self.filepath, self.safe_remove)


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
    return result_file


def parse_lint_result(lint_result_path):
    root = ET.parse(lint_result_path).getroot()
    issues = []
    for issue in root.findall('.//issue[@id="UnusedResources"]'):
        location = issue.find('location')
        filepath = location.get('file')
        # if the location contains line and/or column attribute not the entire resource is unused. that's a guess ;)
        safe_remove = (location.get('line') or location.get('column')) is None
        issues.append(Issue(filepath, safe_remove))
    return issues


if __name__ == '__main__':
    lint_result_path = run_lint_command()
    issues = parse_lint_result(lint_result_path)

