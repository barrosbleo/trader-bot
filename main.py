#https://hpdeandrade.medium.com/crie-seu-primeiro-rob%C3%B4-trader-com-python-e-metatrader5-938f6b620477
#https://medium.com/geekculture/building-a-basic-crypto-trading-bot-in-python-4f272693c375
#https://medium.com/geekculture/beginners-guide-to-technical-analysis-in-python-for-algorithmic-trading-19164fb6149

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import talib.abstract as ta
import datetime as dt
import time


# wallet settings
boughtAssets = []
tickets = {}

# parameters settings
#asset = 'PETR4'
asset = 'ITSA4'
volume = 100.0
interval = mt5.TIMEFRAME_M15 # metaTrader5 15 min interval constant
start = dt.datetime(2022, 10, 15) # year month day
end = dt.datetime.now()


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

def defineStrategy(historicalData):
    # build study values
    BBands = ta.BBANDS(historicalData['Close'], timeperiod = 14, nbdevup = 2.0, nbdevdn = 2.0, matype = 0)
    RSI = ta.RSI(historicalData['Close'], timeperiod = 14)
    
    strategyData = historicalData.copy()
    strategyData['BBUp'] = BBands[0]
    strategyData['BBMedia'] = BBands[1]
    strategyData['BBDown'] = BBands[2]
    strategyData['RSI'] = RSI
    
    # opt 1
    strategyData['BBSignal'] = np.where(strategyData['Close'] < strategyData['BBDown'], 1, np.where(strategyData['Close'] > strategyData['BBUp'], -1, 0))
    strategyData['RSISignal'] = np.where(strategyData['RSI'] > 15, 1, 0)
    strategyData['Decision'] = np.where((strategyData['BBSignal'] == 1) & (strategyData['RSISignal'] == 1), 'Buy', np.where((strategyData['BBSignal'] == -1) & (strategyData['RSISignal'] == 1), 'Sell', 'Wait'))
    # end of opt 1
    
    # opt 2
    #strategyData['BBSignal'] = np.where(strategyData['Close'] < strategyData['BBDown'], 1, np.where(strategyData['Close'] > strategyData['BBUp'], -1, 0))
    #if strategyData['BBSignal'].iloc[-1] == 1:
    #    pass
    #strategyData['RSISignal'] = np.where(strategyData['RSI'] < 30, 1, np.where(strategyData['RSI'] > 70, -1, 0))
    #strategyData['Decision'] = np.where((strategyData['BBSignal'] == 1) & (strategyData['RSISignal'] == 1), 'Buy', np.where((strategyData['BBSignal'] == -1) & (strategyData['RSISignal'] == 1), 'Sell', 'Wait'))
    
    
    
    #print(strategyData['Decision'])
    # end of opt 2
    
    #print(strategyData['Decision'])
    # save CSV to the project folder
    strategyData['RSI'].to_csv('RSI.csv', index = True, encoding = 'utf-8')
    strategyData['Decision'].to_csv('decisionTable.csv', index = True, encoding = 'utf-8')
    strategyData.to_csv(asset + '.csv', index = True, encoding = 'utf-8')
    
    return strategyData



while True:
    currentTime = dt.datetime.now()
    time.sleep(60 - (currentTime.second + currentTime.microsecond/1000000.0))# wait till clock change minute
    #time.sleep(5)
    
    # run MetaTrader5
    if not mt5.initialize():
        print('Initialize() failed, error code =', mt5.last_error())
        mt5.shutdown()
        quit()
    
    # check if chosen asset is available/able on MetaTrader5
    availableAssets = mt5.symbols_get(group = '*' + asset + '*')
    if asset in asset in [availableAssets[n].name for n in range(len(availableAssets))]:
        mt5.symbol_select(asset, True)
    else:
        print('Ativo selectionado inválido. Verifique se o mesmo está disponível na plataforma do MetaTrader5')
    
    # get historicalData
    historicalData = getHistoricalData(asset, interval, start, end)
    
    # get strategy data
    strategyData = defineStrategy(historicalData)
    
    currentTime = dt.datetime.strftime(currentTime, '%Y-%m-%d %H:%M')
    
    if(strategyData['Decision'].iloc[-1] == 'Buy') and (asset not in boughtAssets):
        # fill in buing bill
        buy_bill = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': asset,
            'volume': volume,
            'price': mt5.symbol_info_tick(asset).ask,
            'type': mt5.ORDER_TYPE_BUY,
            'type_filling': mt5.ORDER_FILLING_RETURN,
            'magic': 123456
        }
        
        # send bill to stock and add asset to boughtAsset list
        buy_order = mt5.order_send(buy_bill)
        boughtAssets.append(asset)
        tickets[asset] = buy_order.order
        print('(' + currentTime + ') Comprando ' + str(volume) + ' ' + asset + '...')
    elif(strategyData['Decision'].iloc[-1] == 'Sell') and (asset in boughtAssets):
        # fill in selling bill
        sell_bill = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': asset,
            'volume': volume,
            'type': mt5.ORDER_TYPE_SELL,
            'position': tickets[asset],
            'magic': 123456
        }
        
        # send bill to stock and remove asset from boughtAssets list
        sell_order = mt5.order_send(sell_bill)
        boughtAssets.remove(asset)
        tickets.pop(asset)
        print('(' + currentTime + ') Vendendo ' + str(volume) + ' ' + asset + '...')
    else:
        print('(' + currentTime + ') Aguarde...')
    