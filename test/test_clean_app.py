import os
import unittest
import android_clean_app as clean_app
import tempfile
import xml.etree.ElementTree as ET


class CleanAppTestCase(unittest.TestCase):
    def test_reads_all_unused_resource_issues(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml')
        self.assertEqual(12, len(actual))

    def test_marks_resource_as_save_to_remove(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml')
        remove_entire_file = filter(lambda issue: issue.remove_file, actual)
        self.assertEqual(11, len(remove_entire_file))

    def test_marks_resource_as_not_save_to_remove_if_it_has_used_values(self):
        actual = clean_app.parse_lint_result('./test/android_app/lint-result.xml')
        not_remove_entire_file = filter(lambda issue: not issue.remove_file, actual)
        self.assertEqual(1, len(not_remove_entire_file))

    def test_extracts_correct_info_from_resource(self):
        issues = clean_app.parse_lint_result('./test/android_app/lint-result.xml')
        not_remove_entire_file = filter(lambda issue: not issue.remove_file, issues)
        actual = not_remove_entire_file[0]
        self.assertEqual('res\\values\\strings.xml', actual.filepath)
        self.assertGreater(len(actual.elements), 0)
        self.assertEqual(('string', 'missing'), actual.elements[0])

    def test_removes_given_resources_if_safe(self):
        temp, temp_path = tempfile.mkstemp()
        os.close(temp)

        issue = clean_app.Issue(temp_path, True)

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), False)
        with self.assertRaises(IOError):
            open(temp_path)

    def test_removes_an_unused_value_from_a_file(self):
        temp, temp_path = tempfile.mkstemp()
        os.write(temp, """
            <resources>
                <string name="app_name">android_app</string>
                <string name="missing">missing</string>
                <string name="app_name1">android_app1</string>
            </resources>
        """)
        os.close(temp)

        issue = clean_app.Issue(temp_path, False)
        issue.add_element('The resource R.string.missing appears to be unused')
        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), True)

        root = ET.parse(temp_path).getroot()
        self.assertEqual(2, len(root.findall('string')))

    def test_ignores_layouts(self):
        temp, temp_path = tempfile.mkstemp()
        os.write(temp, """
            <resources>
                <string name="app_name">android_app</string>
                <layout name="missing">missing</layout>
                <string name="app_name1">android_app1</string>
            </resources>
        """)
        os.close(temp)

        issue = clean_app.Issue(temp_path, False)
        issue.add_element('The resource R.string.missing appears to be unused')
        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path), False)

        root = ET.parse(temp_path).getroot()
        self.assertEqual(1, len(root.findall('layout')))


if __name__ == '__main__':
    unittest.main()
