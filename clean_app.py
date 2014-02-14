import argparse
import os
import subprocess


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
        print 'Running the command fail. Try running from the console. Arguments to call: {0}'.format(
            [lint, app_dir, '--xml', result_file])
    return result_file


if __name__ == '__main__':
    lint_result_path = run_lint_command()
    print lint_result_path
