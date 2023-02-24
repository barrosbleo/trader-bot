#Three lines to make our compiler able to draw:
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import talib.abstract as ta
import datetime as dt
import time


# parameters settings
asset = 'PETR4'
interval = mt5.TIMEFRAME_M1 # metaTrader5 15 min interval constant
start = dt.datetime(2022, 11, 17) # year month day
end = dt.datetime.now()

print(int(end.strftime("%H")))
print(int(end.strftime("%M")))

if int(end.strftime("%H")) < 10 and int(end.strftime("%M")) < 5:
    print("Aguarde até as 10:05 horas, horário inicial de operações da Bolsa...")
'''
# function to obtain historical data
def getHistoricalData(asset, interval, start, end):
    
    # download data according to the parameters
    mt5HistoricalData = mt5.copy_rates_range(asset, interval, start, end)
    
    # arrange the data
    historicalData = pd.DataFrame(mt5HistoricalData)
    historicalData.rename(columns={'time': 'Date', 'open': 'Open', 'high' : 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    historicalData['Date'] = pd.to_datetime(historicalData['Date'], unit='s')
    historicalData.set_index('Date', inplace=True)
    historicalData.drop(columns=['spread', 'real_volume'], inplace=True)
    
    return historicalData

# run MetaTrader5
if not mt5.initialize():
    mt5.shutdown()

historicalData = getHistoricalData(asset, interval, start, end)
upper, middle, lower = ta.BBANDS(historicalData['Close'], timeperiod = 20, nbdevup = 2.0, nbdevdn = 2.0)

#plt.plot(historicalData['Close'])
print(upper)
plt.plot(upper)
plt.plot(middle)
plt.plot(lower)

plt.xlabel('Time Interval')
plt.ylabel('Asset Value')

plt.show()

#Two  lines to make our compiler able to draw:
#plt.savefig(sys.stdout.buffer)
#sys.stdout.flush()

'''
