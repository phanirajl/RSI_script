# Test and Method Imports
import unittest
import json
import datetime
from dateutil.tz import tzutc # important for the sample data using this fxn.

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

    def test_rsi_generic_error(self):
        print("\t- Testing Error: RSI_Generic_Error [Default]")
        with self.assertRaises(RSI_Errors.RSI_Generic_Error):
            raise self.my_rsi_generic_error

    # ...

    #-------------------------
    # HTTP 503 Error Tests
    #-------------------------

    def test_http_503_error(self):
        print("\t- Testing Error: HTTP_503_Error [Default]")
        with self.assertRaises(RSI_Errors.HTTP_503_Error):
            raise self.my_http_503_error

    # ...

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
        # Example and Answer provided by Akshay's method. He should double check this just to be sure.
        test_input = [1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70]
        test_result = self.my_rsi.calculateRSI(test_input)
        print("rsi: "+str(test_result))
        self.assertEqual(test_result, 84.31903258988926)

    @unittest.expectedFailure
    def test_error_prices_dict(self):
        print("\t- Testing Error: 'prices' is Dict not List.")
        test_input = {{"close": "10.50" }}
        with self.assertRaises(ValueError):
            test_result = self.my_rsi.help_collect_close_list(test_input)

    @unittest.expectedFailure
    def test_error_prices_length_tto_small(self):
        print("\t- Testing Error: 'prices' length < 15 .")
        test_input = [{"close": "10.50" },{"close": "10.50" },{"close": "10.50" }]
        with self.assertRaises(ValueError):
            test_result = self.my_rsi.help_collect_close_list(test_input)

    # ...

    #---------------------
    # help_collect_close_list() Tests
    #---------------------

    def test_with_example(self):
        print("\t- Testing help_collect_close_list() with Akshay's example data.")
        # Call the method with the example data. Test for the correct answer.
        test_input = [
            {
                'close': 13940.0,
                'foreignNotional': 4873.0,
                'high': 13965.5,
                'homeNotional': 0.3508198699999999,
                'lastSize': 7,
                'low': 13756.5,
                'open': 13784.0,
                'symbol': 'XBTUSD',
                'timestamp': datetime.datetime(2018, 1, 1, 0, 0, tzinfo=tzutc()),
                'trades': 74,
                'turnover': 35081987,
                'volume': 4873,
                'vwap': 13890.8182
            }, {
                'close': 13700.5,
                'foreignNotional': 20502.0,
                'high': 13977.0,
                'homeNotional': 1.48152307,
                'lastSize': 4,
                'low': 13700.0,
                'open': 13940.0,
                'symbol': 'XBTUSD',
                'timestamp': datetime.datetime(2018, 1, 1, 0, 5, tzinfo=tzutc()),
                'trades': 84,
                'turnover': 148152307,
                'volume': 20502,
                'vwap': 13838.915
            }
        ]
        test_result = self.my_rsi.help_collect_close_list(test_input)
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
        # Stop the RSI_Script, and allow it to clean up.
        self.my_rsi.stop()

        # Delete the Helper class, result data, and input data
        self.my_rsi = None

#----------------------------------
# Main Method, to run the unittest
#----------------------------------
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