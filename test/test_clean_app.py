import os
import unittest
import android_clean_app as clean_app
import tempfile
import xml.etree.ElementTree as ET
from mock import MagicMock, patch


class CleanAppTestCase(unittest.TestCase):

    def test_reads_all_unused_resource_issues(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml',
                                             './test/android_app/AndroidManifest.xml')
        self.assertEqual(15, len(actual))

    def test_marks_resource_as_save_to_remove(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml',
                                             './test/android_app/AndroidManifest.xml')
        remove_entire_file = list(filter(lambda issue: issue.remove_file, actual))
        self.assertEqual(11, len(remove_entire_file))

    def test_marks_resource_as_not_save_to_remove_if_it_has_used_values(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml',
                                             './test/android_app/AndroidManifest.xml')
        not_remove_entire_file = list(filter(lambda issue: not issue.remove_file, actual))
        self.assertEqual(4, len(not_remove_entire_file))

    def test_extracts_correct_info_from_resource(self):
        issues = clean_app.parse_lint_result('./test/android_app/lint-result.xml',
                                             './test/android_app/AndroidManifest.xml')
        not_remove_entire_file = list(filter(lambda issue: not issue.remove_file, issues))
        actual = list(filter(lambda issue: os.path.normpath(issue.filepath) == os.path.normpath(
            'res/values/strings.xml'), not_remove_entire_file))[0]
        self.assertGreater(len(actual.elements), 0)
        self.assertEqual(('string', 'missing'), actual.elements[0])

    def test_removes_given_resources_if_safe(self):
        temp, temp_path = tempfile.mkstemp()
        os.close(temp)

        issue = clean_app.Issue(temp_path, True)

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), False)
        with self.assertRaises(IOError):
            open(temp_path)

    def _removes_an_unused_value_from_a_file(self, message, expected_elements_count=2):
        temp, temp_path = tempfile.mkstemp()
        os.write(temp, """
            <resources>
                <string name="app_name">android_app</string>
                <string name="missing">missing</string>
                <string name="app_name1">android_app1</string>
            </resources>
        """.encode('utf-8'))
        os.close(temp)

        issue = clean_app.Issue(temp_path, False)
        issue.add_element(message)
        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), True)

        root = ET.parse(temp_path).getroot()
        self.assertEqual(expected_elements_count, len(root.findall('string')))

    def test_removes_an_unused_value_from_a_file_old_format(self):
        message = 'The resource R.string.missing appears to be unused'
        self._removes_an_unused_value_from_a_file(message)

    def test_removes_an_unused_value_from_a_file_new_format(self):
        message = 'The resource `R.string.missing` appears to be unused'
        self._removes_an_unused_value_from_a_file(message)

    def test_handle_incorrect_missing_resource_pattern(self):
        message = 'Wrong pattern !!!'
        self._removes_an_unused_value_from_a_file(message, 3)

    def test_ignores_layouts(self):
        temp, temp_path = tempfile.mkstemp()
        os.write(temp, """
            <resources>
                <string name="app_name">android_app</string>
                <layout name="missing">missing</layout>
                <string name="app_name1">android_app1</string>
            </resources>
        """.encode('UTF-8'))
        os.close(temp)

        issue = clean_app.Issue(temp_path, False)
        issue.add_element('The resource R.string.missing appears to be unused')
        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), False)

        root = ET.parse(temp_path).getroot()
        self.assertEqual(1, len(root.findall('layout')))

    def test_remove_resource_file_skip_missing_files(self):
        issue = MagicMock()
        issue.elements = [['dummy']]
        with patch('os.remove') as patch_remove:
            clean_app.remove_resource_file(issue, 'dummy', False)
            self.assertFalse(patch_remove.called)

    def test_remove_value_only_if_the_file_still_exists(self):
        temp, temp_path = tempfile.mkstemp()
        os.close(temp)
        os.remove(temp_path)

        issue = clean_app.Issue(temp_path, False)
        issue.add_element('The resource `R.drawable.drawable_missing` appears to be unused')

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), False)

    def test_whitelist_string_refs(self):
        expected = ['app_name']
        res = clean_app.get_manifest_string_refs('./test/android_app/AndroidManifest.xml')
        self.assertEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
