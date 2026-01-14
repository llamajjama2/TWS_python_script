#Testing on the SPY
#things to add:
"""
how this works 
Similar to bot2_resistanceLevel 
this bot has a confirmation price on its short or long before entering a price: 
for example: Level: 500, we enter a short only when it goes down a certain level lets say $2 the confirmation zone

from there we buy when buyers try to re-enter the market to get a better price, the buy logic is the same and the sell logic is the same as well 
vice versa for longs 



"""

from ib_insync import * 
from datetime import datetime



util.startLoop()

#manual config(adjust these) 
LEVELS  = [680.7, 683, 685, 687, 688.45, 689.2, 690.20, 691.70]                #resistance levels 
TOLERANCE =  0.2              #$3 tolerance 
STOP_OFFSET = 0.25           #
QTY = 2                    # 10 shares of SPY $5000 
TP_PERCENT = 0.5            #take profit 50% 
MAX_TRADE_TIME = 60 * 30    #the function does it in seconds 
TP_OFFSET = 0.25            #test 
CONFIRM_DISTANCE = 0.5      #price rejection need to be at from now 
CONFIRM_TIMEOUT = 60




#helper functions get the next level 
def nearest_resistance(price, levels):  
    above = [l for l in levels if l > price]            #LONGS make a list of all resistances greater than price and get the smallest one 
    return min(above) if above else None

def nearest_support(price, levels):
    below = [l for l in levels if l < price]            #SHORT does the opposite of above 
    return max(below) if below else None



#async lets you run multiple things at once without having it to run in sync this can stop freezes 
def main():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    level_state = {}
    for level in LEVELS:
        level_state[level] = {
            "long_confirmed": False,
            "short_confirmed": False,
            "long_time": None,
            "short_time": None
        }


    
    def on_stop_fill(trade): #TEST THISSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
        nonlocal position_open, entry_time, entry_price, position_side, remaining_qty, tp_trade, stop_trade
        print(f"First Stop triggered")
        position_open = False
        entry_time = None
        entry_price = None
        position_side = None
        remaining_qty = 0
        if tp_trade is not None:
            ib.cancelOrder(tp_trade.order)
            tp_trade = None
        stop_trade = None

    ib.reqMarketDataType(3)                        #calls no subscription delayed data 15-20 minutes delayed 
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
        price = ticker.last
        if price is None:
            continue
        
        #print(f"Price: {price}")
        if last_price is None: 
            last_price = price
            continue

        for level in LEVELS:
            # ----------------- SHORT LOGIC (resistance) -----------------
            if not position_open:
                # Step 1: confirmation
                if not level_state[level]["short_confirmed"]:
                    if price <= level - CONFIRM_DISTANCE:
                        level_state[level]["short_confirmed"] = True
                        level_state[level]["short_time"] = datetime.now()
                        print(f"✅ Level {level} SHORT confirmed at {price}")

                # Step 2: rejection after confirmation
                else:
                    rejection = price > last_price  # buyers try to hold 
                    if (datetime.now() - level_state[level]["short_time"]).seconds > CONFIRM_TIMEOUT:
                        level_state[level]["short_confirmed"] = False
                    elif rejection:
                        print(f"🔻 Resistance rejection at {level} — SHORT SPY")

                        print(f"🔻 Resistance bounce at {level} — SHORT SPY")

                        entry_trade = ib.placeOrder(contract, MarketOrder('SELL', QTY, transmit=True))
                        entry_trade.filledEvent
                    
                        entry_price = entry_trade.orderStatus.avgFillPrice
                        print("entry_price")
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
                    level_state[level]["short_confirmed"] = False


            if not position_open:
                # Step 1: confirmation
                if not level_state[level]["long_confirmed"]:
                    if price >= level + CONFIRM_DISTANCE:
                        level_state[level]["long_confirmed"] = True
                        level_state[level]["long_time"] = datetime.now()
                        print(f"✅ Level {level} LONG confirmed at {price}")

                # Step 2: rejection after confirmation
                else:
                    rejection = price < last_price
                    # Optional: cancel confirmation if too old
                    if (datetime.now() - level_state[level]["long_time"]).seconds > CONFIRM_TIMEOUT:
                        level_state[level]["long_confirmed"] = False
                    elif rejection:
                        print(f"🔺 Support bounce at {level} — LONG SPY")

                        entry_trade = ib.placeOrder(contract, MarketOrder('BUY', QTY, transmit=True))
                        entry_trade.filledEvent

                        entry_price = entry_trade.orderStatus.avgFillPrice
                        print("entry_price")
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

                        level_state[level]["long_confirmed"] = False
            
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