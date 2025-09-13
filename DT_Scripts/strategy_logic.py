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
def fib_function(price, low_price, high_price, direction='up', tolerance=0.0): 
    """
    Check if current price is near the 79% Fibonacci retracement/extension.
    
    :param price: current price (float)
    :param low_price: start of move
    :param high_price: end of move
    :param direction: 'up' or 'down' (trend direction)
    :param tolerance: optional range around fib79 to count as a bounce
    :return: (hit_fib79: bool, passed_fib79: bool)
    """
    if direction == 'up':
        fib79 = high_price - (high_price - low_price) * 0.79
        hit = fib79 - tolerance <= price <= fib79 + tolerance
        passed = price < fib79 - tolerance #trend still falling past our line  
    else:  # downtrend
        fib79 = low_price + (high_price - low_price) * 0.79
        hit = fib79 - tolerance <= price <= fib79 + tolerance
        passed = price > fib79 + tolerance #price is still rising past our line

    return hit, passed
#order block function 
def is_ob(bars, direction="bullish", tolerance=0.0): 
    if len(bars) < 3:
        return False, None


    c1, c2, c3 = bars[-3], bars[-2], bars[-1]

    if direction == 'bullish':
        
        if c2.close < c2.open and c3.close > c2.high:
            ob_low = c2.low
            ob_high = c2.high
            tapped = ob_low - tolerance <= c3.low <= ob_high + tolerance
            return tapped, (ob_low, ob_high)

    elif direction == 'bearish':
   
        if c2.close > c2.open and c3.close < c2.low:
            ob_low = c2.low
            ob_high = c2.high
            tapped = ob_low - tolerance <= c3.high <= ob_high + tolerance
            return tapped, (ob_low, ob_high)

    return False, None


current_tend = None 
# change in order flow
#candles: list of dicts with { 'high': float, 'low': float, 'close': float }
def change_of(bar):
    global current-trend
    bos, direction = is_bos(bar) 


    if not bos: 
        return False, None 
    
    if current_trend is None: 
        current_trend = direction 
        return False, None 
    
    if direction != current_trend: 
        print("Change in Order Flow detected at", bar.date, "direction:", direction)
        current_trend = direction
        return True, direction

    current_trend = direction 
    return False, None 




# get the 50% equilibrium for possible selling above is expensive, below is cheap
def equilibrium_level(high, low):
    return (high + low) / 2


def is_at_equilibrium(price, high, low, tolerance=0.1):
    eq = equilibrium_level(high, low)
    return abs(price - eq) <= tolerance, eq



def find_support_resistance(bars, lookback=20, tolerance=0.01):
    highs = [bar.high for bar in bars[-lookback:]]
    lows = [bar.low for bar in bars[-lookback:]]
    
    support_levels = []
    resistance_levels = []

    # Simple swing detection
    for i in range(1, len(highs)-1):
        # Swing High → Resistance
        if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            # Check tolerance grouping
            if not any(abs(highs[i] - r) <= tolerance*highs[i] for r in resistance_levels):
                resistance_levels.append(highs[i])
        # Swing Low → Support
        if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
            if not any(abs(lows[i] - s) <= tolerance*lows[i] for s in support_levels):
                support_levels.append(lows[i])
                
    return support_levels, resistance_levels


def update_flipped_levels(price):
    global flipped_levels
    for s in support_levels:
        if price < s and not any(f['level']==s for f in flipped_levels):
            # Support broken → now potential resistance
            flipped_levels.append({'level': s, 'type': 'support'})
    for r in resistance_levels:
        if price > r and not any(f['level']==r for f in flipped_levels):
            # Resistance broken → now potential support
            flipped_levels.append({'level': r, 'type': 'resistance'})

def check_breaker_block_tap(price):
    for f in flipped_levels:
        lvl = f['level']
        lvl_type = f['type']
        if lvl_type == 'support':  # broken support → resistance
            if lvl*(1 - tolerance) <= price <= lvl*(1 + tolerance):
                return True, lvl, 'Support → Resistance'
        elif lvl_type == 'resistance':  # broken resistance → support
            if lvl*(1 - tolerance) <= price <= lvl*(1 + tolerance):
                return True, lvl, 'Resistance → Support'
    return False, None, None





