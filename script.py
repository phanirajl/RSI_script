import bitmex
import datetime
import logging
import sched, time
import json
import pandas
import pandas_datareader.data
#import talib #pip install TA-Lib


#needs AT LEAST 15 records to run
def calculateRSI(prices):


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


def help_collect_close_list(input_data):
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


client = bitmex.bitmex(api_key="e-821dISZ8iE6BEwgh652dc3", api_secret="Y5ppArBDcE8pwlBHdilQOt32ANp6tMkd_U-1Rk8uiG2GB0Nr")
#dir(client.Quote)
#client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 

listRSI=[False]*101
profitRSI=[False]*101
s = sched.scheduler(time.time, time.sleep)
#run a loop to run this every 2 minutes
def algorithm():
    candles=client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=250, partial=True, startTime=datetime.datetime.now()).result()
    prices=help_collect_close_list(candles[0])
    RSICurrent=calculateRSI(prices)
    LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
    logger=logging.getLogger()
    logger.info(RSICurrent)
    print(RSICurrent)
    print (prices[-1])
    roundedRSI=round(RSICurrent)
    #IMPORTANT NOTE: MAKE SURE ORDER SIZES ARE GREATER THAN 0.0025 XBT OTHERWISE ACCOUNT WILL BE CONSIDERED SPAM
    #Buying low RSI
    if (roundedRSI<=20 and listRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][1]['price']#getting the bid price
        client.Order.Order_new(symbol='XBTUSD', orderQty=30, price=price,execInst='ParticipateDoNotInitiate')
        listRSI[roundedRSI]=True
        logger.info("Buy order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

    #Shorting high RSI
    if (roundedRSI>=85 and listRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][0]['price']#getting the ask price
        client.Order.Order_new(symbol='XBTUSD', orderQty=-30, price=price,execInst='ParticipateDoNotInitiate')
        listRSI[roundedRSI]=True
        logger.info("Short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
    print (listRSI)
##################################################TAKING PROFITS BELOW##################################################################

    #Taking profits
    currency={"symbol": "XBTUSD"}
    position=client.Position.Position_get(filter= json.dumps(currency)).result()
    quantity=position[0][0]["currentQty"]

    #selling a long position
    if (quantity>0 and roundedRSI>=25 and profitRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][0]['price']#getting the ask price
        client.Order.Order_new(symbol='XBTUSD', orderQty=-quantity/10, price=price,execInst='ParticipateDoNotInitiate')
        profitRSI[roundedRSI]=True
        logger.info("Take profit on long order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))

    #covering a long position
    if (quantity<0 and roundedRSI<=77 and profitRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][1]['price']#getting the bid price
        client.Order.Order_new(symbol='XBTUSD', orderQty=quantity/10, price=price,execInst='ParticipateDoNotInitiate')
        profitRSI[roundedRSI]=True
        logger.info("Cover short order placed at :"+str(price)+" For RSI of: "+str(roundedRSI))
    print (profitRSI)

    s.enter(40, 1, algorithm)

s.enter(1, 1, algorithm)
s.run()


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


