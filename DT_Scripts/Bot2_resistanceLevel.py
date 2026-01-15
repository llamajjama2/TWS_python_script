#Testing on the SPY
#things to add:
"""
1. take profit do nearest resistance, with a time in market, with a take profit and a runner 
2. see what trailing stop is 
3.  multiple levels is (find a way to identify the resistance levels manually
4. see candle confirmation is
5. see what time frame to use ( we are using 5 to 15 minute charts)
To do, find resistance levels add take profit, test, adjust, s

when advanced and logic works well add position class and trademanager class

move to QQQ  once we found a good bot 


test normal bot first them look into these one 
look into adding entry_delay
looks interesting 

also we can try setting th sl as our entry (SAME AS THE entry_denlay ONE just make the config the SL level)




first touch is liquid grab trade third or second test







GENERAL additions: price above and below EMA short if < EMA long if price > EMA

TRADE AFTER CANDLE CLOSES 

adapts stops ******
stop = entry_price ± (1.2 * ATR)

run bot only during profitable times 


after a stop out wait 10-30 or wait for a new level 


MAX loss bot shuts off if max loss is hit should do the same for profit 

log stats ***********


"""

from ib_insync import * 
from datetime import datetime, time
import pytz



util.startLoop()

#manual config(adjust these) 
LEVELS  = [680.2, 683.8, 686.6,  688.5, 691.6, 695, 700 ]                #resistance levels 
TOLERANCE =  0.1              #$3 tolerance 
STOP_OFFSET = 0.5           #
QTY = 10                    # 10 shares of SPY $5000 
TP_PERCENT = 0.5            #take profit 50% 
MAX_TRADE_TIME = 60 * 30    #the function does it in seconds 
TP_OFFSET = 0.25            #test 
CONFIRM_DISTANCE = 0.5      #price rejection need to be at from now 
ITERATIONS = 20             
COOLDOWN = 60 * 10
last_trade_time_by_level = {}

US_EASTERN = pytz.timezone("US/Eastern")

def market_is_open():
    now = datetime.now(US_EASTERN).time()
    return time(9, 30) <= now <= time(16, 0)
#return time(9, 30) <= now <= time(15, 30)

#helper functions get the next level 
def nearest_resistance(price, levels):  
    above = [l for l in levels if l > price]            #LONGS make a list of all resistances greater than price and get the smallest one 
    
    return (min(above) +  price) / 2 if above else None

def nearest_support(price, levels):
    below = [l for l in levels if l < price]            #SHORT does the opposite of above 
    return (max(below) +  price) / 2 if below else None



#async lets you run multiple things at once without having it to run in sync this can stop freezes 
def main():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    ib.reqMarketDataType(1)
    def on_stop_fill(trade): #TEST THISSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
        nonlocal position_open, entry_time, entry_price, position_side, remaining_qty, tp_trade, stop_trade
        print(f"Stop triggered")
        print(price)
        position_open = False
        entry_time = None
        entry_price = None
        position_side = None
        remaining_qty = 0
        if tp_trade is not None:
            ib.cancelOrder(tp_trade.order)
            tp_trade = None
        stop_trade = None

                           #calls no subscription delayed data 15-20 minutes delayed 
    contract = Stock('SPY', 'SMART', 'USD')    #SMART uses the best on 
    ib.qualifyContracts(contract)                 # connects it with interactive brokers 

    ticker = ib.reqMktData(contract)                    #gets the current market data live 
    
    tp_trade = None
    stop_trade = None
    last_price = None                                   #checks the last price to detect rejection 
    position_open = False                               #checks if position is ongoing 
    entry_time = None 
    entry_price = None
    position_side = None
    remaining_qty = 0
    confirm_price = None
    last_confirm_time = datetime.now() 

    print(" Bot running...")
    while True:
        ib.sleep(1)
        if not market_is_open():
            continue
        price = ticker.last
        if price is None:
            continue
        #THUYRHDJHRDJDRJDRJDRJDRJDRJDRJRDJJRJDRJDRJRDJDJRRJ
        #print(f"Price: {price}")
        if last_price is None: 
            last_price = price
            continue
        
        


        for level in LEVELS:
            now = datetime.now()
            if level in last_trade_time_by_level:
                if (now - last_trade_time_by_level[level]).seconds < COOLDOWN:
                    continue

            
            in_zone = (level - TOLERANCE) <= price <= (level + TOLERANCE)
            
            if in_zone and not position_open:
                if price < level:  # approaching from below → resistance SHORTTTTTTT
                    rejection = (level - price) >= CONFIRM_DISTANCE  # price starts falling
                    if rejection:
                        print(f"🔻 Resistance bounce at {level} — SHORT SPY")

                        entry_trade = ib.placeOrder(contract, MarketOrder('SELL', QTY, transmit=True))
                        entry_trade.filledEvent
                        last_trade_time_by_level[level] = now

                        entry_price = entry_trade.orderStatus.avgFillPrice
                        entry_time = datetime.now()
                        position_side = "SHORT"
                        position_open = True
                        stop_price = level + STOP_OFFSET
                        remaining_qty = QTY
           

                        stop_trade = ib.placeOrder(contract, StopOrder('BUY', QTY, stop_price, transmit=True))  # stop loss 
                        stop_trade.filledEvent += on_stop_fill

                        tp_level = nearest_support(level, LEVELS)
                        if tp_level:
                            tp_qty = int(QTY * TP_PERCENT)
                            tp_trade = ib.placeOrder(contract, LimitOrder('BUY', tp_qty, tp_level + TP_OFFSET, transmit=True))
                            def on_tp_fill(trade):
                                nonlocal remaining_qty, stop_trade
                                remaining_qty -= trade.orderStatus.filled
                                print(f"🎯 TP filled: remaining_qty={remaining_qty}")

                                # cancel old stop and place new one for remaining shares
                    
                                ib.cancelOrder(stop_trade.order)
                                if remaining_qty > 0:
                                    stop_trade = ib.placeOrder(contract, StopOrder('BUY', remaining_qty, tp_level + STOP_OFFSET, transmit=True))
                                    stop_trade.filledEvent += on_stop_fill
                            tp_trade.filledEvent += on_tp_fill


                elif price > level:         # approaching from above → support LONGGGGGGGG 
                    rejection = price > last_price  # price starts rising
                    if rejection:
                        print(f"🔺 Support bounce at {level} — LONG SPY")

                        entry_trade = ib.placeOrder(contract, MarketOrder('BUY', QTY, transmit=True))
                        entry_trade.filledEvent
                        last_trade_time_by_level[level] = now
                        entry_price = entry_trade.orderStatus.avgFillPrice
                        entry_time = datetime.now()
                        position_side = "LONG"
                        position_open = True
                        stop_price = level - STOP_OFFSET
                        remaining_qty = QTY

                        stop_trade = ib.placeOrder(contract, StopOrder('SELL', QTY, stop_price, transmit=True ))        # stop loss 
                        stop_trade.filledEvent += on_stop_fill

                        tp_level = nearest_resistance(level, LEVELS)
                        if tp_level:
                            tp_qty = int(QTY * TP_PERCENT)          #tp_qty is 50%                    
                            tp_trade = ib.placeOrder(contract, LimitOrder('SELL', tp_qty, tp_level - TP_OFFSET, transmit=True))   #sell 50% of longs         
                            def on_tp_fill(trade):
                                nonlocal remaining_qty, stop_trade
                                remaining_qty -= trade.orderStatus.filled
                                print(f"🎯 TP filled: remaining_qty={remaining_qty}")

                                # cancel old stop and place new one for remaining shares
                                
                                ib.cancelOrder(stop_trade.order)
                                if remaining_qty > 0:
                                    stop_trade = ib.placeOrder(contract, StopOrder('SELL', remaining_qty, tp_level - STOP_OFFSET, transmit=True))
                                    stop_trade.filledEvent += on_stop_fill
                            tp_trade.filledEvent += on_tp_fill
                        

        
        last_price = price
        if position_open and entry_time:
            elapsed = (datetime.now() - entry_time).total_seconds()
            if elapsed > MAX_TRADE_TIME: 
                print("Time exit — closing position")
                ib.placeOrder(contract, MarketOrder('SELL' if position_side == "LONG" else 'BUY', remaining_qty, transmit=True))
                #test 
                ib.cancelOrder(stop_trade.order)
                if tp_trade:
                    ib.cancelOrder(tp_trade.order)


                position_open = False
                entry_time = None
                position_side = None
                remaining_qty = 0

if __name__ == "__main__":
    main()

ib.disconnect()