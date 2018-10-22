import bitmex
import datetime
#import talib #pip install TA-Lib

client = bitmex.bitmex(api_key="xz6A_yXiAJgNB9YAZF-jvvOY", api_secret="obXhEbnAPDFV__s_tBMuy0JiHC7jLdbJI_OSWvsnFThmSkVt")
dir(client.Quote)
client.OrderBook.OrderBook_getL2(symbol="XBTUSD").result() 
client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=10, startTime=datetime.datetime(2018, 1, 1)).result()


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


    return([avgGain,avgLoss,changes,RSI])
	
calculateRSI([1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,16,17,11,12,12,14,15,16,11,1,2,3,40,50,60,70])