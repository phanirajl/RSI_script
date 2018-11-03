import bitmex
import datetime
import logging
import sched, time
import json
import pandas # MUST BE PANDAS 0.19.2 FOR THIS TO WORK
import pandas_datareader.data
import configparser
from importlib import reload
import os

# Import RSI Errors
import RSI_Errors

# Extras
from colorama import init, deinit, Fore, Back, Style


# Objectifying the Script
class RSI_Script(object):

    # Class variables
    isAkshay = False # Flag determining if current user is Akshay or Barrett? Use appropriate files/settings for each.
    LOG_FORMAT = "%(levelname)s - %(asctime)s - %(message)s" # String defining the format for both log files to br written in.  

    # Initialization method. Called when a new instance of the RSI_Script object is created.
    def __init__(self):
        
        # Surround main initialization in a keyboard interrupt except.
        try:

            # Init Colorama, reset style chars after every message.
            init(autoreset=True)
            
            #Reload logging module.
            reload(logging)

            # Initialize config as object variables.
            self.config = configparser.ConfigParser()

            # Check which developer's settings to use. Grab key, secret, and client_test.
            if RSI_Script.isAkshay:
                logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.DEBUG, format=RSI_Script.LOG_FORMAT)
                self.config.read("my_config.ini")
                self.key = str(self.config['Keys'].get('akshay_api_key'))
                self.secret = str(self.config['Keys'].get('akshay_api_secret'))
                self.client_test = bool(self.config['Keys'].get('client_test', 'False')) # Akshay's default will be test=False. i.e. Real money!
            else:
                filename = str(datetime.datetime.now()).replace(":","-").replace(".","_").replace(",","_").replace(" ","_")[:-7]#cheap hack, will fix later
                filepath = os.path.join("C:\\Users\\Barrett\\Documents\\SmartGit\\Akshay\\RSI_script\\logs",filename+".log")
                logging.basicConfig(filename=filepath, level=logging.DEBUG, format=RSI_Script.LOG_FORMAT)
                self.config.read("barrett_config.ini")
                self.key = str(self.config['Keys'].get('barrett_api_key'))
                self.secret = str(self.config['Keys'].get('barrett_api_secret'))
                self.client_test = bool(self.config['Keys'].get('client_test', 'True')) # Barrett's default will be test=True. i.e. No way in hell i'm using real money that's not mine!

            # Initialize logger as an object variable as well.
            self.logger=logging.getLogger()

            # Initialize client as an object variable too. 
            self.client = bitmex.bitmex(test=self.client_test ,api_key=self.key, api_secret=self.secret)

            # Akshay added this change.
            self.CURRENT_POSITION=2040

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
            
            # Initalize Scheduler, schedule a trip to the "algorithm" in a sec, and then run it!
            self.printl("Initializing the scheduler.", True)
            self.s = sched.scheduler(time.time, time.sleep)
            
            #self.s.enter(1, 1, self.algorithm)
            #self.s.enter(3, 1, self.dummy)
            # self.s.run()

            self.getbxresponse()

        except KeyboardInterrupt:
            # Program was interrupted by user.
            self.printl("So you wanna stop, eh? Must not like money very much...", logging.WARNING, True)

        except Exception as e:
            # Some other excemption has occured, and is being genericaly handled here.
            self.printl("[X]    Some unhandled exception has occured. "+str(e), logging.ERROR, True)

        finally:
            self.printl("Cleaning up.", True)
            
            # De-init Colorama
            deinit()

    # Dummy method
    def dummy(self):
    
        #Testing 4 types of outputs
        self.printl("Debug",logging.DEBUG,True)
        self.printl("Info",logging.INFO,True)
        self.printl("Warning",logging.WARNING,True)
        self.printl("Error",logging.ERROR,True)
        
        # Testing custom errors
        self.printl("About to raise and handle an error!", True)
        try:
            self.printl("When you try your best and you....", True)
            #raise RSI_Errors.RSI_Generic_Error("...don't suceeed!")
            raise RSI_Errors.RSI_Generic_Error()

        except RSI_Errors.RSI_Generic_Error as e:
            self.printl(str(e),logging.ERROR)

        finally:
            self.printl("Handler complete.",True)
        
        # Return true, because why not!
        return True

    # Test Method
    def getbxresponse(self):
        bxres = self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=250, partial=True, startTime=datetime.datetime.now())
        print("bxres is "+str(type(bxres)))
        bxresult = bxres.result()
        print("bxresult is "+str(type(bxresult))+" and has len "+str(len(bxresult)))
        print("bxresult[0] is "+str(type(bxresult[0]))+" and has len "+str(len(bxresult[0])))
        print("bxresult[1] is "+str(type(bxresult[1]))) # RRA has no len 
        print("bxresult[0][0] is "+str(type(bxresult[0][0])))
        print("bxresult[0][1] is "+str(type(bxresult[0][1])))
        print("RRA status_code: "+str(bxresult[1].status_code))
        print("RRA reason: "+str(bxresult[1].reason))
        #print("RRA text: "+str(bxresult[1].text)) # this is the content, scrap
        print("RRA headers: "+str(bxresult[1].headers))
        #print("bxresult[1][0] is "+str(type(bxresult[1][0])))
    

    # Log and Print helper method
    def printl(self, message, level=logging.INFO, toConsole=False):
        if level == logging.INFO: # Normal
            self.logger.info(message) 
            if toConsole: print(Style.NORMAL + message)
        elif level == logging.DEBUG: # Cyan, Dim
            self.logger.debug(message)
            if toConsole: print(Style.DIM + Fore.CYAN + message)
        elif level == logging.ERROR: # Red, Bright!
            self.logger.error(message)
            if toConsole: print(Style.BRIGHT + Fore.RED + message)
        elif level == logging.WARNING: # Yellow
            self.logger.warning(message)
            if toConsole: print(Style.NORMAL + Fore.YELLOW + message)           

    # Helper
    def bitmex_response_helper(self, response_object, silent=False):
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
            http_headers = response_object[1].headers

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

                
    # Helper to calculate the "close" values of each record in the incoming list
    def help_collect_close_list(self, input_data):
        """
        Helper method, in order to isolate the "close" values of each record in the incoming list.
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

        #Return the list of 'close' prices
        return close_list

    #needs AT LEAST 15 records to run
    def calculateRSI(self, prices):
        window_length = 14

        # Create a panda series with the incoming prices.
        close=pandas.Series(prices)
        
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

    #run a loop to run this every 2 minutes
    def algorithm(self):

        # Switching from defining these as globals to referenceing them as the object variables they now are (with self.variable_name).
        #global profitRSI, listRSI, orders, prevorderProfit, prevorderCover

        candles = self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=250, partial=True, startTime=datetime.datetime.now()).result()
        prices = self.help_collect_close_list(candles[0])
        RSICurrent = self.calculateRSI(prices)
        self.logger.info(RSICurrent)
        self.printl(RSICurrent, True)
        self.printl(prices[-1], True)
        roundedRSI = int(round(RSICurrent))
        #IMPORTANT NOTE: MAKE SURE ORDER SIZES ARE GREATER THAN 0.0025 XBT OTHERWISE ACCOUNT WILL BE CONSIDERED SPAM
        #Buying low RSI
        if (roundedRSI <= 20 and self.listRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][1]['price']#getting the bid price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=30, price=price,execInst='ParticipateDoNotInitiate').result() #Need .result() in order for the order to go through
            self.orders = self.orders+","+result[0]['orderID']
            self.listRSI[roundedRSI] = True
            self.logger.info("Buy order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

        #Shorting high RSI
        if (roundedRSI >= 80 and self.listRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][0]['price'] # getting the ask price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-30, price=price,execInst='ParticipateDoNotInitiate').result()
            self.orders = self.orders+","+result[0]['orderID']
            self.listRSI[roundedRSI] = True
            self.logger.info("Short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

        #TODO: MAKE SURE THAT TAKE PROFIT LEVELS HAVE ORDER SIZES OF ABOVE 0.0025 BTC (around $16 right now).
        ###################################TAKING PROFITS BELOW##################################################

        #Taking profits
        currency = {"symbol": "XBTUSD"}
        position = self.client.Position.Position_get(filter= json.dumps(currency)).result()
        quantity = position[0][0]["currentQty"]+self.CURRENT_POSITION

        #selling a long position
        if (quantity > 0 and roundedRSI >= 25 and self.profitRSI[roundedRSI ]== False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][0]['price'] # getting the ask price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-30, price=price,execInst='ParticipateDoNotInitiate').result()
            if (self.prevorderProfit and self.prevorderProfitPrice != price):
                self.client.Order.Order_cancel(orderID=self.prevorderProfit).result()
                #logger.info("Cancelled existing order for taking profit")
            self.prevorderProfit = result[0]['orderID']
            self.prevorderProfitPrice = price
            self.profitRSI[roundedRSI] = True
            self.logger.info("Take profit on long order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
        
        #cleaning up orders and position arrays
        if(roundedRSI > 40 and roundedRSI < 60 and quantity == 0):
            if self.orders:
                self.client.Order.Order_cancel(orderID=self.orders).result() # CANCEL ALL ACTIVE ORDERS
                self.orders=""
                self.logger.info("Cancelled existing orders")
            self.listRSI = [False]*101
            self.profitRSI = [False]*101
            self.logger.info("Resetted position arrays for RSI of: "+str(roundedRSI))

        #covering a short position
        if (quantity < 0 and roundedRSI <= 75 and self.profitRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][1]['price'] # getting the bid price
            result=self.client.Order.Order_new(symbol='XBTUSD', orderQty=30, price=price,execInst='ParticipateDoNotInitiate').result()
            if (self.prevorderCover and self.prevorderCoverPrice != price):
                self.client.Order.Order_cancel(orderID=self.prevorderCover).result()
                #logger.info("Cancelled existing order for covering short")
            self.prevorderCover = result[0]['orderID']
            self.prevorderCoverPrice=price
            self.profitRSI[roundedRSI] = True
            self.logger.info("Cover short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
        self.printl(self.listRSI, True)
        self.printl(self.profitRSI, True)

        # TODO?: Should this still be here Akshay? 
        self.s.enter(40, 1, self.algorithm)

###########################################
#calculateRSI([1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70])

#import threading

# def printit():
#   threading.Timer(5.0, printit).start()
#   print "Hello, World!"

# printit()


