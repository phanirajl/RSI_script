import bitmex
import datetime
import logging
import sched, time
import json
import pandas
import pandas_datareader.data
import configparser
#import talib #pip install TA-Lib
from importlib import reload


# Objectifying the Script
class RSI_Script(object):

    # Class variables

    isAkshay = False # Flag determining if current user is Akshay or Barrett? Use appropriate files/settings for each.
    LOG_FORMAT = "%(levelname)s - %(asctime)s - %(message)s" # String defining the format for both log files to br written in.
    

    # Initialization method. Called when a new instance of the RSI_Script object is created.
    def __init__(self, filename):

        #Reload logging module.
        reload(logging)

        # Initialize config as object variables.
        self.config = configparser.ConfigParser()

        # Check which developer's settings to use. Grab key, secret, and client_test.
        if RSI_Script.isAkshay:
            logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.INFO, format=RSI_Script.LOG_FORMAT)
            self.config.read("my_config.ini")
            self.key = str(self.config['Keys'].get('akshay_api_key'))
            self.secret = str(self.config['Keys'].get('akshay_api_secret'))
            self.client_test = bool(self.config['Keys'].get('client_test', 'False')) # Akshay's default will be test=False. i.e. Real money!
        else:
            logging.basicConfig(filename='C:\\Users\\Barrett\\Documents\\SmartGit\\Akshay\\RSI_script\\logs\\'+str(datetime.datetime.now())+".log", level=logging.INFO, format= RSI_Script.LOG_FORMAT)
            self.config.read("barrett_config.ini")
            self.key = str(self.config['Keys'].get('barrett_api_key'))
            self.secret = str(self.config['Keys'].get('barrett_api_secret'))
            self.client_test = bool(self.config['Keys'].get('client_test', 'True')) # Barrett's default will be test=True. i.e. No way in hell i'm using real money that's not mine!

        # Initialize logger as an object variable as well.
        self.logger=logging.getLogger()

        # Initialize client as an object variable too. 
        self.client = bitmex.bitmex(test=self.client_test ,api_key=self.key, api_secret=self.secret)

        # Here are some important object variables that will be used in the "algorithm",
        # and need initializing here (apparently). 
        self.prevorderProfit=""
        self.prevorderCover=""
        self.orders=""
        #dir(client.Quote)
        #client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        self.listRSI=[False]*101
        self.profitRSI=[False]*101
        
        # Initalize Scheduler, schedule a trip to the "algorithm" in a sec, and then run it!
        self.s = sched.scheduler(time.time, time.sleep)
        #self.s.enter(1, 1, self.algorithm)
        self.s.enter(3, 1, self.dummy)
        self.s.run()

    # Dummy method
    def dummy(self):
        self.logger.info("Hello World! "+str(datetime.datetime.now()))
        return True

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

    def help_collect_close_list(self, input_data):
        """
        Helper method, in order to isolate the "close" values of each record in the incoming list.
        """
        close_list = []
        #print(json.dumps(input_data[0], indent=4))

        # Check input_data is a List
        if type(input_data) is not list:
            print("Error: parameter 'input_data' must be a List, not a "+str(type(input_data))+".")
            raise TypeError("parameter 'input_data' must be a List, not a "+str(type(input_data))+".")

        # Check incoming List for each 'record' dictionary of data.
        if len(input_data)>0:
            # Iterate through each record, check for its 'close' price, and append to close_list
            for record in input_data:
                if "close" in record.keys():
                    close_list.append(record.get("close"))
                else:
                    print("Error: Record has no key attribute with name '"+"close"+"'.")
                    raise ValueError("Record has no key attribute with name '"+"close"+"'.")
        else:
            print("Error: parameter 'input_data' list is empty.")
            raise ValueError("parameter 'input_data' list is empty.")

        #Return the list of 'close' prices
        return close_list

    #run a loop to run this every 2 minutes
    def algorithm(self):
        global profitRSI, listRSI, orders, prevorderProfit, prevorderCover
        candles = self.client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=250, partial=True, startTime=datetime.datetime.now()).result()
        prices = self.help_collect_close_list(candles[0])
        RSICurrent = self.calculateRSI(prices)
        self.logger.info(RSICurrent)
        print(RSICurrent)
        print(prices[-1])
        roundedRSI = int(round(RSICurrent))
        #IMPORTANT NOTE: MAKE SURE ORDER SIZES ARE GREATER THAN 0.0025 XBT OTHERWISE ACCOUNT WILL BE CONSIDERED SPAM
        #Buying low RSI
        if (roundedRSI <= 20 and listRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][1]['price']#getting the bid price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=30, price=price,execInst='ParticipateDoNotInitiate').result() #Need .result() in order for the order to go through
            orders = orders+","+result[0]['orderID']
            listRSI[roundedRSI] = True
            self.logger.info("Buy order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

        #Shorting high RSI
        if (roundedRSI >= 80 and listRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][0]['price'] # getting the ask price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-30, price=price,execInst='ParticipateDoNotInitiate').result()
            orders = orders+","+result[0]['orderID']
            listRSI[roundedRSI] = True
            self.logger.info("Short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

        #TODO: MAKE SURE THAT TAKE PROFIT LEVELS HAVE ORDER SIZES OF ABOVE 0.0025 BTC (around $16 right now). So let's say $20 each order, which means buys of $200 rather than $30
        ##################################################TAKING PROFITS BELOW##################################################################

        #Taking profits
        currency = {"symbol": "XBTUSD"}
        position = self.client.Position.Position_get(filter= json.dumps(currency)).result()
        quantity = position[0][0]["currentQty"]+1860

        #selling a long position
        if (quantity > 0 and roundedRSI >= 25 and profitRSI[roundedRSI ]== False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][0]['price'] # getting the ask price
            result = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-30, price=price,execInst='ParticipateDoNotInitiate').result()
            if prevorderProfit:
                self.client.Order.Order_cancel(orderID=prevorderProfit).result()
                #logger.info("Cancelled existing order for taking profit")
            prevorderProfit = result[0]['orderID']
            profitRSI[roundedRSI] = True
            self.logger.info("Take profit on long order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
        if(roundedRSI > 40 and roundedRSI < 60 and quantity == 0):
            if orders:
                self.client.Order.Order_cancel(orderID=orders).result() # CANCEL ALL ACTIVE ORDERS
                orders=""
                self.logger.info("Cancelled existing orders")
            listRSI = [False]*101
            profitRSI = [False]*101
            self.logger.info("Resetted position arrays for RSI of: "+str(roundedRSI))

        #covering a short position
        if (quantity < 0 and roundedRSI <= 75 and profitRSI[roundedRSI] == False):
            level2Result = self.client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
            price = level2Result[0][1]['price'] # getting the bid price
            result=self.client.Order.Order_new(symbol='XBTUSD', orderQty=30, price=price,execInst='ParticipateDoNotInitiate').result()
            if prevorderCover:
                self.client.Order.Order_cancel(orderID=prevorderCover).result()
                #logger.info("Cancelled existing order for covering short")
            prevorderCover = result[0]['orderID']
            profitRSI[roundedRSI] = True
            self.logger.info("Cover short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
        print(listRSI)
        print(profitRSI)

        # TODO?: Should this still be here Akshay? 
        self.s.enter(40, 1, self.algorithm)

###########################################
#calculateRSI([1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70])

#for logging in Ipython:


#In [14]: from importlib import reload

#In [15]: reload(logging)

# In [8]: import logging
#    ...: LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
#    ...: logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
#    ...: logger=logging.getLogger()
#    ...: logger.warning('This message should go to the log file')
#    ...: logger.level

#import threading

# def printit():
#   threading.Timer(5.0, printit).start()
#   print "Hello, World!"

# printit()


