
from ib_insync import * 
from datetime import datetime



util.startLoop()



#first touch is liquid grab trade third or second test

#manual config(adjust these)
LEVELS  = []                #resistance levels 
TOLERANCE =  0.2            #$3 tolerance 
STOP_OFFSET = 0.5            #CONFIGURE TO YOUR NEW LEVELS
QTY = 2                     # 10 shares of SPY $5000 
TP_PERCENT = 0.5            #take profit 50% 
MAX_TRADE_TIME = 60 * 30    #the function does it in seconds 
TP_OFFSET = 0.25            #test 
CONFIRM_DISTANCE = 0.5      #price rejection need to be at from now 
ITERATIONS = 20             






def main():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    ib.reqMarketDataType(3)                        #calls no subscription delayed data 15-20 minutes delayed 
    contract = Stock('SPY', 'SMART', 'USD')    #SMART uses the best on 
    ib.qualifyContracts(contract)                 # connects it with interactive brokers 

    ticker = ib.reqMktData(contract)                    #gets the current market data live

    






































