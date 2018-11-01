# Test and Method Imports
import unittest
import json
# Example-Required Imports
import datetime
import RSI_Script

class TestRSIScriptMethods(unittest.TestCase):
    """
    Implements a unittest TestCase in order to test the "script.py" methods.
    """

    def setUp(self):
        # Reinitialize the Custom class
        self.my_rsi = RSI_Script()
    
    def test_with_example(self):
        print("\t- Testing [Method Name]")
        test_input = {some real data here}
        test_result = self.my_rsi.method_to_test(test_input)
        self.assertEqual(test_result, correct answer here)

    @unittest.expectedFailure
    def test_error_non_list(self):
        print("\t- Testing Error: [Method Name]")
        test_input = {some real data here}
        with self.assertRaises(TypeErrorToCheckFor):
            test_result = self.my_rsi.help_collect_close_list(test_input)

    def tearDown(self):
        # Delete the Helper class, result data, and input data
        self.my_rsi = None
        self.test_result = None
        self.test_input = None

if __name__ == '__main__':
    print("> Beginning Unit Testing.")
    unittest.main()