""" 
1. What I need high and low of 1d, 4h, 1h as take profit points DONE

2.make a function boolean to check if there is a reversal, above yesterdays high or lower than yesterdays low then break back into the known zone 

3. Once a sweep get the data for the 1 and 5 minute can use the same function as get_high_low 

4. make a function to look for FVG so with the data given from the 1 and 5 minutes check if theres a FVG with a boolean function we prob want to set that to higher than the last 3 candle bars or lower 

5. make a boolean function for Break of structure, like a reversal but we need to check if it goes below the previous low after a high rally and vice versa 

6.  honestly just hard code support bands

7. Most important is 79% fib extension dk how tf to implement this 

8 then check stuff again and GO 

"""
#get the high and lows of any market bar  
def get_high_low(contract, duration, bar_size):
    """
    Fetch historical bars and return the high and low.
    :param contract: IB Contract (e.g., Stock)
    :param duration: How far back (e.g., '1 D', '2 D')
    :param bar_size: Bar size (e.g., '1 hour', '4 hours', '1 day')
    """
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='TRADES',
        useRTH=True,     
        formatDate=1
    )
    if not bars:
        return None, None
    
    high = max(bar.high for bar in bars)
    low = min(bar.low for bar in bars)
    return high, low



#Get the 1 minute and 5 minute data continuously 
def get_data():
    bars = ib.reqRealTimeBars(contract, 60, "TRADES", useRTH=True)
    return bars

def get_minutes_data(contract, ib):
    ticker = ib.reqMktData(contract, '', snapshot=False, regulatorySnapshot=False)
    ib.sleep(2)  # give IBKR a moment to send data

    if not ticker:
        return None

    return ticker


def get_historical_data(contract, duration, bar_size):
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='TRADES',
        useRTH=True,     
        formatDate=1
    )
    if not bars:
        return None, None
    return high, low

#WARNING TEST FOR BOTH reqMktData and the reqHistoricalData
def is_FVG(bars): 
    if len(bars) < 3: 
        return False, None
    
    c1, c2, c3 = bars[-3], bars[-2], bars[-1]

    if c1.high < c3.low:
        return True, "Bullish"

    if c1.low > c3.high:
        return True, "Bearish"
    
    return False, None 
"""
to call just type found, fvg_type = check_fvg(bars)
where found is the bool and fvg_type is None or Bearish/bullish 
"""


#trend change break above previous high or low
def is_bos(bar):
    global last_high, last_low
    if(bar.high > last_high):
        print("BOS Up detected at", bar.date, "high:", bar.high)
        last_high = bar.high
        return True, "Uptrend"
    if(bar.low < last_low):
        print("BOS Down detected at", bar.date, "low:", bar.low)
        last_low = bar.low
        return True, "Downtrend"    
    return False, None


#79% fib function 




