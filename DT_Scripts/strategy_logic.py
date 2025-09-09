""" 
1. What I need high and low of 1d, 4h, 1h as take profit points DONE

2.make a function boolean to check if there is a reversal, above yesterdays high or lower than yesterdays low then break back into the known zone 

3. Once a sweep get the data for the 1 and 5 minute can use the same function as get_high_low 

4. make a function to look for FVG so with the data given from the 1 and 5 minutes check if theres a FVG with a boolean function we prob want to set that to around 0.5% change 

5. make a boolean function for Break of structure, like a reversal but we need to check if it goes below the previous low after a high rally and vice versa 

6.  honestly just hard code support bands

7. Most important is 79% fib extension dk how tf to implement this 

8 then check stuff again and GO 




"""

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



def is_FVG(bar_data): 
    if():
        return True 

    

    return False 




