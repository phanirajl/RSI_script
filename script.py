import bitmex
import datetime
import logging
import sched, time
#import talib #pip install TA-Lib


#needs AT LEAST 15 records to run
def calculateRSI(prices):
    changes=[]
    avgGain=0
    avgLoss=0
    for x,price in enumerate(prices):
        if(x==0):
            x=1
        changes.append(int(price)-int(prices[x-1]))
    for x,change in enumerate(changes):
        if change>0:
            avgGain+=change
        else:
            avgLoss+=-change
        if x==14:
            break
    avgGainInitial=avgGain/14
    avgLossInitial=avgLoss/14
    changes=changes[14:]
    avgGain=[]
    avgLoss=[]
    RSI=[]
    avgGain.append(avgGainInitial)
    avgLoss.append(avgLossInitial)
    for x,change in enumerate(changes):
        if x==0:
            continue
        currentGain=0
        currentLoss=0
        if change>0:
            currentGain=change
        else:
            currentLoss=-change
        avgGain.append((avgGain[x-1]*13+currentGain)/14)
        avgLoss.append((avgLoss[x-1]*13+currentLoss)/14)
        if (avgLoss[x]*13+currentLoss)==0:
            RSI.append(100)
        else:
            smoothedRS=avgGain[x]/avgLoss[x]
            RSI.append(100-(100/(1+smoothedRS)))


    return(RSI[-1])



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


client = bitmex.bitmex(api_key="", api_secret="")
dir(client.Quote)
#client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 


s = sched.scheduler(time.time, time.sleep)
#run a loop to run this every 2 minutes
def algorithm():
    candles=client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=100, partial=True, startTime=datetime.datetime.now()).result()
    prices=help_collect_close_list(candles[0])
    RSICurrent=calculateRSI(prices)
    LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
    logger=logging.getLogger()
    logger.info(RSICurrent)
    print(RSICurrent)
    roundedRSI=round(RSICurrent)
    listRSI=[False]*101
    #Buying low RSI
    if (roundedRSI<=20 and listRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][1]['price']#getting the bid price
        client.Order.Order_new(symbol='XBTUSD', orderQty=10, price=price,execInst='ParticipateDoNotInitiate').result()
        listRSI[roundedRSI]==True
        logger.info("Buy order placed at :"+str(price))
        
    #Shorting high RSI
    if (roundedRSI>=80 and listRSI[roundedRSI]==False):
        level2Result=client.OrderBook.OrderBook_getL2(symbol="XBTUSD",depth=1).result() 
        price=level2Result[0][0]['price']#getting the ask price
        client.Order.Order_new(symbol='XBTUSD', orderQty=-10, price=price,execInst='ParticipateDoNotInitiate').result()
        listRSI[roundedRSI]==True
        logger.info("Short order placed at :"+str(price))

    s.enter(120, 1, algorithm)

s.enter(1, 1, algorithm)
s.run()


###########################################
#calculateRSI([1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70])

#for logging in Ipython:


#In [14]: from importlib import reload

#In [15]: reload(logging)

# In [8]: import logging^M
#    ...: LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
#    ...: logging.basicConfig(filename='C:\\Users\\micha_000\\Documents\\BitMexBot\example.log',level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')^M
#    ...: logger=logging.getLogger()
#    ...: logger.warning('This message should go to the log file')
#    ...: logger.level

#import threading

# def printit():
#   threading.Timer(5.0, printit).start()
#   print "Hello, World!"

# printit()

# # continue with the rest of your code
