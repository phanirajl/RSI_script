#!/usr/bin/python3
import configparser
import bitmex
import datetime
from datetime import timedelta
from datetime import timezone
from importlib import reload
import json
import logging
import pandas #NOTE:MUST BE PANDAS 0.19.2 FOR THIS TO WORK
import pandas_datareader.data
import os
import time
import traceback

# Import RSI Errors
import RSI_Errors
from RSI_Timezone_Helper import RSI_Timezone

# Extras
from colorama import init, deinit, Fore, Back, Style

#Experimental
from django.core.serializers.json import DjangoJSONEncoder #https://stackoverflow.com/a/11875813
#import pytz
#from pytz import timezone as pytztimezone

# Objectifying the Script
class RSI_Script(object):
    """
    This is the object that encompasses the trading logic itself. It can be instantiated with "from script import RSI_Script".
    """
    
    # Class Constants ("class variables", affect all instances of a class)
    LOG_FORMAT = "%(levelname)s - %(asctime)s - %(message)s" # String defining the format for both log files to br written in.  
    
    # Initialization method. Called when a new instance of the RSI_Script object is created.
    def __init__(self, selected_timezone,coin_symbol,quantity):
        
        # Reload logging module.
        reload(logging)

        # Instance of RSI_Timezone
        self.my_rsi_timezone = RSI_Timezone()

        self.coin_symbol=coin_symbol
        self.trade_quantity=quantity

        # The selected timezone for the rest of the application to use.
        #NOTE: Note the logger doesn't use this yet.
        self.SELECTED_TIMEZONE = selected_timezone
        
        # Flag determining if current user is Akshay or Barrett? Use appropriate files/settings for each.
        self.isAkshay = True

        # Init Colorama, reset style chars after every message.
        init(autoreset=True)

        

        # Initialize config as an object variable.
        self.config = configparser.ConfigParser()

        # Check which developer's settings to use. Grab key, secret, and client_test.

        LOG_DESTINATION = os.path.join(os.getcwd(), os.path.join("logs", self.coin_symbol+".log")) # Akshay's logs now write to the project's directory, in a folder called "logs" (added to gitignore).
        logging.basicConfig(filename=LOG_DESTINATION,level=logging.DEBUG, format=RSI_Script.LOG_FORMAT)

        self.key = "WEvbIq1kwfl3r0utSjTiSJwR"
        self.secret = "k35qBUMz0pqti-aM-0Chw130VCWQOqbe4etuX91hQVh9TKc_"

        self.logger=logging.getLogger()



        try: 
            self.client = bitmex.bitmex(api_key=self.key, api_secret=self.secret)
        except Exception as e:
            # Print an error to log, raise custom Bitmex Client error with error string.
            self.printl("[X]    The Bitmex client failed to initialize in __init__ method.", logging.ERROR, True)
            raise RSI_Errors.Bitmex_Client_Error(str(e))

                # Check the selected timezone, and pick the correct timedelta offset.
        if self.my_rsi_timezone.get_current_datetime_in_timezone(self.SELECTED_TIMEZONE).tzname() == "Kelowna":
            self.printl("Algorithm using the Kelowna timezone.", logging.DEBUG, True)
            self.SELECTED_OFFSET = RSI_Timezone.TIMEDELTA_KELOWNA
            self.SELECTED_OFFSET = -timedelta(hours=0)
        elif self.my_rsi_timezone.get_current_datetime_in_timezone(self.SELECTED_TIMEZONE).tzname() == "Toronto":
            self.printl("Algorithm using the Toronto timezone.", logging.DEBUG, True)
            self.SELECTED_OFFSET = RSI_Timezone.TIMEDELTA_TORONTO
        else:
            self.SELECTED_OFFSET = RSI_Timezone.TIMEDELTA_KELOWNA
            self.printl("Algorithm defaulting to Kelowna timezone due to unrecognized timezone.", logging.DEBUG, True)


        # Akshay added this change for TestMex specifically.
        self.CURRENT_POSITION=0

        # Here are some important object variables that will be used in the "algorithm",
        # and need initializing here (apparently). 
        self.prevorderProfit=""
        self.prevorderCover=""
        self.orders=""
        self.prevorderProfitPrice=0
        self.prevorderCoverPrice=0
        #dir(client.Quote)
        #client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        self.listRSI=[False]*101
        self.profitRSI=[False]*101

        self.prices=None
              

    def run(self):
        """
        This method is used to run and start trading in the currency specified by the coin_symbol string.

        Attributes:
            coin_symbol -- This is the string of the symbol for the currency that you wish to trade in. Ex "XBTUSD" for Bitcoin USD .
        """
        #self.printl("Running RSI_Script.", logging.DEBUG, True)

        # Surround main initialization in a keyboard interrupt except.
        try:
            
            # Simulate work.
            # print("[~~~~~AKSHAY's AWESOME CODE GOES HERE~~~~~~~]")
            # time.sleep(2)

            # Run the algorithm: the real work.
            self.algorithm()

        except KeyboardInterrupt:
            # Program was interrupted by user.
            self.printl("So you wanna stop, eh? Must not like money very much...", logging.WARNING, True)
            # Re-raise Keyboard Interrupt for run_script's try/except to handle it.
            raise KeyboardInterrupt()

        except Exception as e:
            # Some other excemption has occured, and is being genericaly handled here.
            self.printl("[X]    Some unhandled exception has occured. "+str(e), logging.ERROR, True)
            self.printl(str(traceback.print_exc(e)), logging.ERROR, True) # Decoration not applied.

        #finally:
            #self.stop()

    def stop(self):
        self.printl("Stopping RSI_Script.", logging.DEBUG, True)

        # De-init Colorama
        #deinit()

        # Close the log file
        logging.shutdown()

    # Log and Print helper method.
    def printl(self, message, level=logging.INFO, toConsole=False):
        """
        This method is a helper to be able to write information to both the 'console' AND 
        the 'log' file. It's so that way you can "write it once", and have it outputed twice
        if needed (cleaning up a bit of the code).
        
        Attributes:
            message -- This is the text to be shown.
            level -- This is the logging level to use. Must be a constant of the logging class.
            toConsole -- This boolean flag describes if you want the message to be printed to the console in addition to the log file.
        """
        if level == logging.INFO: # Normal
            self.logger.info(message) 
            if toConsole: print(Style.NORMAL + Fore.GREEN + message)
        elif level == logging.DEBUG: # Cyan, Dim
            self.logger.debug(message)
            if toConsole: print(Style.DIM + Fore.CYAN + message)
        elif level == logging.ERROR: # Red, Bright!
            self.logger.error(message)
            if toConsole: print(Style.BRIGHT + Fore.RED + message)
        elif level == logging.WARNING: # Yellow
            self.logger.warning(message)
            if toConsole: print(Style.NORMAL + Fore.YELLOW + message)           

    # Helper to raise custom exceptions in Bitmex response objects.
    def bitmex_response_helper(self, response_object, silent=False):
        """
        This method is used to read the response from the Bitmex client, and look at the status
        of the response. If the call has failed (ie. HTTP status != 200), it will log it, and
        can raise the specific HTTP erro exception, providing the exact details from the 
        response.
        
        Attributes:
            response_object -- This is the output of the "self.client.XXXXXX().result()" call.
            silent -- A flag to control whether python errors are raised by this method. Logs will always be written.
        """
        # respponse_object <class 'tuple'>, length 2
        # respponse_object[0] <class 'list'>, length N (this is how many data items there are)
        # respponse_object[0][0] <class 'dict'> length M (this is how many attributes each item has)
        # response_object[1] <class 'bravado.requests_client.RequestsResponseAdapter'>
        #       https://bravado.readthedocs.io/en/stable/bravado.html#bravado.requests_client.RequestsResponseAdapter

        #Type validation, response_object must be 'tuple'.
        if type(response_object) is not tuple:
            self.printl("Error: parameter 'response_object' must be a Tuple, not a "+str(type(response_object))+".", logging.ERROR, True)
            raise TypeError("parameter 'input_data' must be a List, not a "+str(type(response_object))+".")

        # Grab http code, check for success 200
        http_status = int(response_object[1].status_code)
        if http_status == 200:
            return
        else:
            # We have a non-success. Grab relevant information
            http_reason = response_object[1].reason
            #http_headers = response_object[1].headers #header can be used if needed in future.

            # Without silence, we throw an error
            if http_status == 400:
                self.printl("Bitmex Response Helper: Recieved a HTTP 400 result. "+http_reason)
                if not silent: raise RSI_Errors.HTTP_400_Error("Bitmex Response Helper: Recieved a HTTP 400 result.", http_reason)
            elif http_status == 403:
                self.printl("Bitmex Response Helper: Recieved a HTTP 403 result. "+http_reason)
                if not silent: raise RSI_Errors.HTTP_403_Error("Bitmex Response Helper: Recieved a HTTP 403 result.", http_reason)
            elif http_status == 503:
                self.printl("Bitmex Response Helper: Recieved a HTTP 503 result. "+http_reason)
                if not silent: raise RSI_Errors.HTTP_503_Error("Bitmex Response Helper: Recieved a HTTP 503 result.", http_reason)
               
    # Helper to calculate the "close" values of each record in the incoming list.
    def help_collect_close_list(self, input_data):
        """
        Helper method, in order to isolate the "close" values of each record in the incoming list.

        Attributes:
            input_data -- This is the List of records that need
        """
        close_list = []
        #print(json.dumps(input_data[0], indent=4))

        # Check input_data is a List
        if type(input_data) is not list:
            self.printl("Error: parameter 'input_data' must be a List, not a "+str(type(input_data))+".", logging.ERROR, True)
            raise TypeError("parameter 'input_data' must be a List, not a "+str(type(input_data))+".")

        # Check incoming List for each 'record' dictionary of data.
        if len(input_data)>0:
            # Iterate through each record, check for its 'close' price, and append to close_list
            for record in input_data:
                if "close" in record.keys():
                    close_list.append(record.get("close"))
                else:
                    self.printl("Error: Record has no key attribute with name '"+"close"+"'.", logging.ERROR, True)
                    raise ValueError("Record has no key attribute with name '"+"close"+"'.")
        else:
            self.printl("Error: parameter 'input_data' list is empty.", logging.ERROR, True)
            raise ValueError("parameter 'input_data' list is empty.")

        # for item in close_list:
        #     print(str(item))
        
        #Return the list of 'close' prices
        return close_list

    # Helper to print out the price data
    def help_print_prices(self, prices, toConsole=True):
        # Validate prices input: List & len >= 15
        if type(prices) is not list:
            self.printl("Error: parameter 'prices' must be a List, not a "+str(type(prices))+".", logging.ERROR, True)
            raise TypeError("parameter 'prices' must be a List, not a "+str(type(prices))+".")

        # Iterate through all records, json string dumping all key, values. 
        self.printl("++ PRINTING PRICES:", logging.info, toConsole)
        for record in prices:
            #NOTE: The use of cls=DjangoJSONEncoder to handle object serialization failures using the Django stategy.
            string_record = json.dumps(record, indent=4, cls=DjangoJSONEncoder)
            self.printl(string_record, logging.INFO, toConsole)

        # Check incoming prices List for the minimum length of required data.
        #self.printl("calculateRSI: Length: "+str(len(prices))+".", logging.INFO, True)
        if not len(prices)>=15:
            self.printl("Error: parameter 'prices' list must have a length >= 15, but has a length of only "+str(len(prices))+".", logging.ERROR, True)
            raise ValueError("Error: parameter 'prices' list must have a length >= 15, but has a length of only "+str(len(prices))+".")

    # Calculates the RSI for a Price List. #NOTE: Needs AT LEAST 15 records to run, which is now validated in the method.
    def calculateRSI(self, prices):
        """
        Method to calculate the RSI of a input set of prices.

        Attributes:
            prices -- These are the prices to calcualte the RSI from. Data type must be an "array-like", dict, or scalar value, according to the "pandas.Series" method's 'data' parameter.
        """
        # Validate prices input: List & len >= 15
        if type(prices) is not list:
            self.printl("Error: parameter 'prices' must be a List, not a "+str(type(prices))+".", logging.ERROR, True)
            raise TypeError("parameter 'prices' must be a List, not a "+str(type(prices))+".")

        # Check incoming prices List for the minimum length of required data.
        #self.printl("calculateRSI: Length: "+str(len(prices))+".", logging.INFO, True)
        if not len(prices)>=15:
            self.printl("Error: parameter 'prices' list must have a length >= 15, but has a length of only "+str(len(prices))+".", logging.ERROR, True)
            raise ValueError("Error: parameter 'prices' list must have a length >= 15, but has a length of only "+str(len(prices))+".")
        
        close=pandas.Series(prices)

        window_length = 14

        # Get the difference in price from previous step
        delta = close.diff()

        # Get rid of the first row, which is NaN since it did not have a previous 
        # row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA
        roll_up1 = pandas.stats.moments.ewma(up, window_length)
        roll_down1 = pandas.stats.moments.ewma(down.abs(), window_length)

        # Calculate the RSI based on EWMA
        RS1 = roll_up1 / roll_down1
        RSI1 = 100.0 - (100.0 / (1.0 + RS1))

        # # Calculate the SMA
        # roll_up2 = pandas.rolling_mean(up, window_length)
        # roll_down2 = pandas.rolling_mean(down.abs(), window_length)

        # # Calculate the RSI based on SMA
        # RS2 = roll_up2 / roll_down2
        # RSI2 = 100.0 - (100.0 / (1.0 + RS2))

        return RSI1.iloc[-1]

    # Akshay's trading algorithm.
    def algorithm(self):
        print(Style.BRIGHT + Fore.BLUE+ "For coin "+str(self.coin_symbol)+":")
        """
        This is Akshay's trading algorithm, which is commented inline.

        Attributes:
            coin_symbol -- This is the string of the symbol for the currency that you wish to trade in. Ex "XBTUSD" for Bitcoin USD .
        """
        # Switching from defining these as globals to referenceing them as the object variables they now are (with self.variable_name).
        #global profitRSI, listRSI, orders, prevorderProfit, prevorderCover
        
        #print("OUR DATETIME: "+str(datetime.datetime.now(tz=self.SELECTED_TIMEZONE)))
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=80, partial=True, startTime=datetime.datetime.now()).result()
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, startTime=datetime.datetime.now(tz=self.SELECTED_TIMEZONE)).result()
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, startTime=datetime.datetime.now(tz=datetime.timezone.utc)).result()
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, startTime=datetime.datetime(year=2018, month=11, day=4, hour=12, minute=0, second=0, tzinfo=self.SELECTED_TIMEZONE)).result()
        #//!@# New Recommendation for acquiring Candles. Note: endTime parameter with custom datetime
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, endTime=datetime.datetime.now(tz=self.SELECTED_TIMEZONE)).result()
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, endTime=datetime.datetime.now()).result()
        #relevant_datetime = self.my_rsi_timezone.get_current_datetime_in_timezone(selected_timezone=self.SELECTED_TIMEZONE)
        #print("Our relevant datatime is: "+str(relevant_datetime))
        #candles=self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=15, partial=True, endTime=relevant_datetime).result()


        
        # Get the correct candles, using the above set SELECTED OFFSET.
        candles = self.client.Trade.Trade_getBucketed(symbol=self.coin_symbol, binSize="5m", count=250, partial=True, startTime=datetime.datetime.utcnow()-timedelta(hours=19)).result()        
        # Helper to print out the candles, log only.
        #self.help_print_prices(candles[0], False)
        
        self.prices=self.help_collect_close_list(candles[0])
        RSICurrent=self.calculateRSI(self.prices)
        self.printl("RSICurrent: "+str(RSICurrent), logging.INFO, True)
        self.printl("price: "+str(self.prices[-1]), logging.INFO, True)
        roundedRSI=int(round(RSICurrent))
        #IMPORTANT NOTE: MAKE SURE ORDER SIZES ARE GREATER THAN 0.0025 XBT OTHERWISE ACCOUNT WILL BE CONSIDERED SPAM
        #Buying low RSI
        if (roundedRSI<=20 and self.listRSI[roundedRSI]==False):
            level2Result=self.client.OrderBook.OrderBook_getL2(symbol=self.coin_symbol,depth=1).result() 
            price=level2Result[0][1]['price']#getting the bid price
            result=self.client.Order.Order_new(symbol=self.coin_symbol, orderQty=self.trade_quantity, price=price,execInst='ParticipateDoNotInitiate').result() #Need .result() in order for the order to go through
            if self.orders:
                self.orders=self.orders+","+result[0]['orderID']
            else:
                self.orders=result[0]['orderID']
            
            self.listRSI[roundedRSI]=True
            self.printl("Buy order placed at :"+str(price)+" For RSI of: "+str(roundedRSI), logging.ERROR, True)

        #Shorting high RSI
        if (roundedRSI>=80 and self.listRSI[roundedRSI]==False):
            level2Result=self.client.OrderBook.OrderBook_getL2(symbol=self.coin_symbol,depth=1).result() 
            price=level2Result[0][0]['price']#getting the ask price
            result=self.client.Order.Order_new(symbol=self.coin_symbol, orderQty=-self.trade_quantity, price=price,execInst='ParticipateDoNotInitiate').result()
            if self.orders:
                self.orders=self.orders+","+result[0]['orderID']
            else:
                self.orders=result[0]['orderID']
            self.listRSI[roundedRSI]=True
            self.printl("Short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI), logging.ERROR, True)

        #TODO: MAKE SURE THAT TAKE PROFIT LEVELS HAVE ORDER SIZES OF ABOVE 0.0025 BTC (around $16 right now).
        ##################################################TAKING PROFITS BELOW##################################################################

        #Taking profits
        currency={"symbol": self.coin_symbol}
        position=self.client.Position.Position_get(filter= json.dumps(currency)).result()
        quantity=position[0][0]["currentQty"]+self.CURRENT_POSITION

        #selling a long position
        if (quantity>0 and roundedRSI>=30 and self.profitRSI[roundedRSI]==False):
            level2Result=self.client.OrderBook.OrderBook_getL2(symbol=self.coin_symbol,depth=1).result() 
            price=level2Result[0][0]['price']#getting the ask price
            result=self.client.Order.Order_new(symbol=self.coin_symbol, orderQty=-self.trade_quantity, price=price,execInst='ParticipateDoNotInitiate').result()
            if self.prevorderProfit and self.prevorderProfitPrice != price:
                self.client.Order.Order_cancel(orderID=self.prevorderProfit).result()
                #self.printl("Cancelled existing order for taking profit", logging.INFO, True)
            self.prevorderProfit=result[0]['orderID']
            self.prevorderProfitPrice=price
            self.profitRSI[roundedRSI]=True
            self.printl("Take profit on long order placed at :"+str(price)+" For RSI of: "+str(roundedRSI), logging.ERROR, True)

        #cleaning up orders and position arrays
        if(roundedRSI>40 and roundedRSI<60 and quantity==0):
            if self.orders:
                self.client.Order.Order_cancel(orderID=self.orders).result() #CANCEL ALL ACTIVE ORDERS
                self.orders=""
                self.printl("Cancelled existing orders", logging.DEBUG, True)
            self.listRSI=[False]*101
            self.profitRSI=[False]*101
            self.printl("Resetted position arrays for RSI of: "+str(roundedRSI), logging.ERROR, True)

        #covering a short position
        if (quantity<0 and roundedRSI<=70 and self.profitRSI[roundedRSI]==False):
            level2Result=self.client.OrderBook.OrderBook_getL2(symbol=self.coin_symbol,depth=1).result() 
            price=level2Result[0][1]['price']#getting the bid price
            result=self.client.Order.Order_new(symbol=self.coin_symbol, orderQty=self.trade_quantity, price=price,execInst='ParticipateDoNotInitiate').result()
            if self.prevorderCover and self.prevorderCoverPrice != price:
                self.client.Order.Order_cancel(orderID=self.prevorderCover).result()
                #self.printl("Cancelled existing order for covering short", logging.DEBUG, True)
            self.prevorderCover=result[0]['orderID']
            self.prevorderCoverPrice=price
            self.profitRSI[roundedRSI]=True
            self.printl("Cover short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI), logging.ERROR, True)
        print("self.listRSI: "+str(self.listRSI))
        print("self.profitRSI: "+str(self.profitRSI))
        
        # Removing the sleeping from the algorithm, placing into the run_script.
        #time.sleep(40)

###########################################
#calculateRSI([1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70])
#For ipython testing
# import bitmex
# import datetime
# from datetime import timezone
# from datetime import timedelta
# selfkey = "WEvbIq1kwfl3r0utSjTiSJwR"
# selfsecret = "k35qBUMz0pqti-aM-0Chw130VCWQOqbe4etuX91hQVh9TKc_"
# client= bitmex.bitmex(api_key=selfkey, api_secret=selfsecret)
# candles = client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=250, partial=True, startTime=datetime.datetime.utcnow()-timedelta(hours=19)).result()        

# import json
# coin_symbol="XBTUSD"
# currency={"symbol": coin_symbol}
# position=client.Position.Position_get(filter= json.dumps(currency)).result()
# #position[0][0]["currentQty"]


