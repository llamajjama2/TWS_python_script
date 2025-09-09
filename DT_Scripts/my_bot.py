from ib_insync import * 
from strategy_logic import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1) 


contract = Stock('AAPL', 'SMART', 'USD')
qualified = ib.qualifyContracts(contract)
print(qualified)



# 1 Day high/low (daily candles)
day_high, day_low = get_high_low(contract, '1 D', '1 day')

# 4 Hour high/low (within last 1 day, 4-hour candles)
h4_high, h4_low = get_high_low(contract, '1 D', '4 hours')

# 1 Hour high/low (within last 1 day, hourly candles)
h1_high, h1_low = get_high_low(contract, '1 D', '1 hour')

print("1 Day High/Low:", day_high, day_low)
print("4 Hour High/Low:", h4_high, h4_low)
print("1 Hour High/Low:", h1_high, h1_low)




ib.disconnect()










 




