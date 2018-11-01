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
        print("\t- Testing Akshay's example data.")
        # Call the method with the example data. Test for the correct answer.
        test_result = self.my_rsi.help_collect_close_list(self.my_rsi.example_value)
        self.assertEqual(test_result, [13940.0, 13700.5])

    @unittest.expectedFailure
    def test_error_non_list(self):
        print("\t- Testing Error: Parameter non-List.")
        test_input = {{'close': 13700.5, 'foreignNotional': 20502.0}}
        with self.assertRaises(TypeError):
            test_result = self.my_rsi.help_collect_close_list(test_input)
    
    @unittest.expectedFailure
    def test_error_no_records(self):
        print("\t- Testing Error: No records in List.")
        test_input = {{}}
        with self.assertRaises(ValueError):
            test_result = self.my_rsi.help_collect_close_list(test_input)
    
    @unittest.expectedFailure
    def test_error_no_close_key(self):
        print("\t- Testing Error: No key 'close' in record.")
        test_input = {{'foreignNotional': 20502.0}}
        with self.assertRaises(ValueError):
            test_result = self.my_rsi.help_collect_close_list(test_input)

    def tearDown(self):
        # Delete the Helper class, result data, and input data
        self.my_rsi = None
        self.test_result = None
        self.test_input = None

if __name__ == '__main__':
    print("> Beginning Unit Testing.")
    unittest.main()