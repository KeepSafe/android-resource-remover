import os
import unittest
import clean_app
import tempfile


class CleanAppTestCase(unittest.TestCase):
    def test_reads_all_unused_resource_issues(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        self.assertEqual(12, len(actual))

    def test_marks_resource_as_save_to_remove(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        remove_entire_file = filter(lambda issue: issue.remove_entire_file, actual)
        self.assertEqual(11, len(remove_entire_file))

    def test_marks_resource_as_not_save_to_remove_if_it_has_used_values(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        not_remove_entire_file = filter(lambda issue: not issue.remove_entire_file, actual)
        self.assertEqual(1, len(not_remove_entire_file))

    def test_extracts_correct_info_from_resource(self):
        issues = clean_app.parse_lint_result('./android_app/lint-result.xml')
        not_remove_entire_file = filter(lambda issue: not issue.remove_entire_file, issues)
        actual = not_remove_entire_file[0]
        self.assertEqual('res\\values\\strings.xml', actual.filepath)
        self.assertFalse(actual.remove_entire_file)
        self.assertEqual(1, len(actual.elements))
        self.assertEqual('missing', actual.elements[0])

    def test_removes_given_resources_if_safe(self):
        temp, temp_path = tempfile.mkstemp()
        os.close(temp)

        issue = clean_app.Issue(temp_path, True)

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path))
        with self.assertRaises(IOError):
            open(temp_path)

    def test_leaves_given_resources_if_not_safe(self):
        temp, temp_path = tempfile.mkstemp()
        os.close(temp)

        issue = clean_app.Issue(temp_path, False)

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path))
        with open(temp_path) as res:
            self.assertIsNotNone(res)


if __name__ == '__main__':
    unittest.main()
