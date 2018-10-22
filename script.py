import bitmex
import datetime
#import talib #pip install TA-Lib

client = bitmex.bitmex(api_key="xz6A_yXiAJgNB9YAZF-jvvOY", api_secret="obXhEbnAPDFV__s_tBMuy0JiHC7jLdbJI_OSWvsnFThmSkVt")
dir(client.Quote)
client.OrderBook.OrderBook_getL2(symbol="XBTUSD").result() 
client.Trade.Trade_getBucketed(symbol="XBTUSD", binSize="5m", count=10, startTime=datetime.datetime(2018, 1, 1)).result()

#need to pass exactly 15 prices to this function
def calculateInitial(prices):
	changes=[]
	avgGain=0
	avgLoss=0
    for x,price in enumerate(prices):
    	if(x==0):
    		x=1
    	print(x)
    	changes.append(int(price)-int(prices[x-1]))
    for change in changes:
    	if change>0:
    		avgGain+=change
    	else:
    		avgLoss+=-change
    avgGain=avgGain/14
    avgLoss=avgLoss/14
    return([avgGain,avgLoss,prices])

def calculateRSI(avgGain,avgLoss,prices,newPrice):
	change=newPrice-prices[14]
	prices.pop(0)
	prices.append(newPrice)
	currentGain=0
	currentLoss=0
	if change>0:
		currentGain=change
	else:
		currentLoss=-change
	if (avgLoss*13+currentLoss)==0:
		RSI=100
	else:
		smoothedRS=((avgGain*13+currentGain)/14)/((avgLoss*13+currentLoss)/14)
		RSI=100-(100/(1+smoothedRS))
	avgGain=0
	avgLoss=0
	changes=[]
	for x,price in enumerate(prices):
    	if(x==0):
    		x=1
    	print(x)
    	changes.append(int(price)-int(prices[x-1]))
    for change in changes:
    	if change>0:
    		avgGain+=change
    	else:
    		avgLoss+=-change
    avgGain=avgGain/14
    avgLoss=avgLoss/14
	return [RSI,avgGain,avgLoss,prices]
	
calculateRSI(1.2857,0.2857,[1, 1, 1, 3, 2, 4, 5, 2, 4, 6, 7, 8, 9, 10, 15],13)