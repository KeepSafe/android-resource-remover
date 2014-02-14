import unittest
import clean_app


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


if __name__ == '__main__':
    unittest.main()
