from ib_insync import *
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

util.startLoop()

LEVELS = [670, 675, 680, 685, 690, 695]
TOLERANCE = 1.0
STOP_OFFSET = 0.5
QTY = 10
MAX_TRADE_TIME = 60 * 45

def nearest_resistance(price, levels):
    above = [l for l in levels if l > price]
    return min(above) if above else None

def nearest_support(price, levels):
    below = [l for l in levels if l < price]
    return max(below) if below else None

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

contract = Stock('SPY', 'SMART', 'USD')
ib.qualifyContracts(contract)

bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='10 D',
    barSizeSetting='2 mins',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1
)

df = util.df(bars)
df.set_index('date', inplace=True)

trades = []
last_price = None
position_open = False
entry_time = None
entry_price = None
position_side = None
stop_price = None
tp_level = None

for time, row in df.iterrows():
    price = row['close']

    if last_price is None:
        last_price = price
        continue
 
    # ENTRY
    if not position_open:
        for level in LEVELS:
            in_zone = (level - TOLERANCE) <= price <= (level + TOLERANCE)

            # SHORT
            if in_zone and price < last_price:
                
                entry_price = price
                stop_price = level + STOP_OFFSET
                tp_level = nearest_support(level, LEVELS)
                entry_time = time
                position_side = "SHORT"
                position_open = True
                break

            # LONG
            elif in_zone and price > last_price:
                
                entry_price = price
                stop_price = level - STOP_OFFSET
                tp_level = nearest_resistance(level, LEVELS)
                entry_time = time
                position_side = "LONG"
                position_open = True
                break

    # MANAGEMENT
    if position_open:
        # STOP
        bar_high = row['high']
        bar_low = row['low']

# For LONG TP
        

        if position_side == "SHORT" and price >= stop_price:
            trades.append(("STOP_SHORT", entry_price, price))
            position_open = False

        elif position_side == "LONG" and price <= stop_price:
            trades.append(("STOP_LONG", entry_price, price))
            position_open = False

        elif position_side == "LONG" and tp_level and bar_high >= tp_level:
            trades.append(("TP_LONG", entry_price, tp_level))
            position_open = False

        # For SHORT TP
        elif position_side == "SHORT" and tp_level and bar_low <= tp_level:
            trades.append(("TP_SHORT", entry_price, tp_level))
            position_open = False

        # TIME EXIT
        elif (time - entry_time).total_seconds() > MAX_TRADE_TIME:
            trades.append(("TIME_EXIT", entry_price, price))
            position_open = False

    last_price = price

results = pd.DataFrame(trades, columns=["type", "entry", "exit"])
results["pnl"] = results.apply(
    lambda r: r["entry"] - r["exit"] if "SHORT" in r["type"] else r["exit"] - r["entry"],
    axis=1
)

print(results)
#print(df)
print("Total PnL:", results["pnl"].sum())
