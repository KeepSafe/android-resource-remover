import os
import unittest
import clean_app
import tempfile


class CleanAppTestCase(unittest.TestCase):
    def test_reads_all_unused_resource_issues(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        self.assertEqual(8, len(actual))

    def test_marks_resource_as_save_to_remove(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        safe_to_remove = filter(lambda issue: issue.safe_remove, actual)
        self.assertEqual(7, len(safe_to_remove))

    def test_marks_resource_as_not_save_to_remove_if_it_has_used_values(self):
        actual = clean_app.parse_lint_result('./android_app/lint-result.xml')
        not_safe_to_remove = filter(lambda issue: not issue.safe_remove, actual)
        self.assertEqual(1, len(not_safe_to_remove))

    def test_extracts_correct_info_from_resource(self):
        issues = clean_app.parse_lint_result('./android_app/lint-result.xml')
        not_safe_to_remove = filter(lambda issue: not issue.safe_remove, issues)
        actual = not_safe_to_remove[0]
        self.assertEqual('res\\values\\strings.xml', actual.filepath)
        self.assertFalse(actual.safe_remove)
        self.assertIsNotNone(actual.message)

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
        issue.add_message('testing')

        clean_app.remove_unused_resources([issue], os.path.dirname(temp_path))
        with open(temp_path) as res:
            self.assertIsNotNone(res)


if __name__ == '__main__':
    unittest.main()
