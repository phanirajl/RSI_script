# Test and Method Imports
import unittest
import json
import datetime

# RSI Script
import script as RSI_File
# Errors
import RSI_Errors


class TestRSIScriptErrors(unittest.TestCase):
    """
    Implements a unittest TestCase in order to test the "RSI_Error.py" contained error classes.
    """

    def setUp(self):
        # Reinitialize the Custom Error classes with NO MESSAGES.
        self.my_rsi_generic_error = RSI_Errors.RSI_Generic_Error()
        self.my_http_503_error = RSI_Errors.HTTP_503_Error()
    
    #-------------------------
    # RSI_Generic_Error Tests
    #-------------------------

    @unittest.expectedFailure
    def test_rsi_generic_error(self):
        print("\t- Testing Error: RSI_Generic_Error [Default]")
        with self.assertRaises(RSI_Errors.RSI_Generic_Error):
            raise self.my_rsi_generic_error

    def tearDown(self):
        # Delete the Custom Error classes.
        self.my_rsi_generic_error = None
        self.my_http_503_error = None



class TestRSIScriptMethods(unittest.TestCase):
    """
    Implements a unittest TestCase in order to test the "RSI_Script" class methods.
    """

    def setUp(self):
        # Reinitialize the Custom class
        self.my_rsi = RSI_File.RSI_Script()
    
    #---------------------
    # calculateRSI() Tests
    #---------------------

    def test_calculateRSI_with_example(self):
        print("\t- Testing calculateRSI() with example.")
        # Example and Answer provided by Akshay.
        test_input = [1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70]
        test_result = self.my_rsi.calculateRSI(test_input)
        self.assertEqual(test_result, 69) #//!@#This is no the real answer by the way...Need to figure out what is...

    def tearDown(self):
        # Delete the Helper class, result data, and input data
        self.my_rsi = None
        self.test_result = None
        self.test_input = None

if __name__ == '__main__':
    print("> Beginning Unit Testing.")
    unittest.main()


#EXAMPLE TEST TEMPLATES

    # @unittest.expectedFailure
    # def test_error_non_list(self):
    #     print("\t- Testing Error: [Method Name]")
    #     test_input = {some real data here}
    #     with self.assertRaises(TypeErrorToCheckFor):
    #         test_result = self.my_rsi.help_collect_close_list(test_input)

    # def test_with_example(self):
    #     print("\t- Testing [Method Name]")
    #     test_input = {some real data here}
    #     test_result = self.my_rsi.method_to_test(test_input)
    #     self.assertEqual(test_result, correct answer here)