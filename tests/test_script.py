# Test and Method Imports
import unittest
import json
# Example-Required Imports
import datetime
import RSI_Script
# Errors
import RSI_Errors


class TestRSIScriptErrors(unittest.TestCase):
    """
    Implements a unittest TestCase in order to test the "RSI_Error.py" classes.
    """

    def setUp(self):
        # Reinitialize the Custom Error classes with NO MESSAGES.
        self.my_rsi_generic_error = RSI_Generic_Error()
        self.my_http_503_error = HTTP_503_Error()
    
    @unittest.expectedFailure
    def test_rsi_generic_error(self):
        print("\t- Testing Error: RSI_Generic_Error [Default]")
        with self.assertRaises(RSI_Generic_Error):
            raise self.my_rsi_generic_error

    def tearDown(self):
        # Delete the Custom Error classes.
        self.my_rsi_generic_error = None
        self.my_http_503_error = None

class TestRSIScriptMethods(unittest.TestCase):
    """
    Implements a unittest TestCase in order to test the "script.py" methods.
    """

    def setUp(self):
        # Reinitialize the Custom class
        self.my_rsi = RSI_Script()
    
    # def test_with_example(self):
    #     print("\t- Testing [Method Name]")
    #     test_input = {some real data here}
    #     test_result = self.my_rsi.method_to_test(test_input)
    #     self.assertEqual(test_result, correct answer here)

    # @unittest.expectedFailure
    # def test_error_non_list(self):
    #     print("\t- Testing Error: [Method Name]")
    #     test_input = {some real data here}
    #     with self.assertRaises(TypeErrorToCheckFor):
    #         test_result = self.my_rsi.help_collect_close_list(test_input)

    def tearDown(self):
        # Delete the Helper class, result data, and input data
        self.my_rsi = None
        self.test_result = None
        self.test_input = None

if __name__ == '__main__':
    print("> Beginning Unit Testing.")
    unittest.main()