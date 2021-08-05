# competition rule
# price = open price
# every minute, 1 lot, horizon = 15,30,60 min
# earn price difference between buy and execute price
# call option, expect price increase
# put options, expect price decrease

# to maximize, determine best horizon and option type every minute
import requests
import yfinance as yf
from ac import auto
import pandas as pd


team = 'w2mak'
pw = 'E999AA9F'
bank = 1e6
buy_call_ratio = 0.75


def buy(ttype, horizon, lots):
  params = {'type':ttype, 'horizon':horizon, 'lots':lots, 'team':team.lower(), 'pass':pw}
  r = requests.post(url="http://api.forecast.university:7707/buy", params=params)
  ret = r.text
  print(ret)

def test():
  params = {'team':team.lower(), 'pass':pw}
  r = requests.get(url="http://api.forecast.university:7707/test", params=params)
  ret = r.text
  print(ret)

def getBank():
  r = requests.get(url="http://api.forecast.university:7707/funds")
  return float(pd.Series(r.text).str.extract('<td>w2mak</td><td>\$(.+)</td>', expand=False).str.replace(',','').iloc[0])

def getPrice():
  x = yf.Ticker("TWOU").history(start="2021-08-01", interval="1m")
  return x["Open"].iloc[-1]

def make_first_trade():
  test()
  latest_price = getPrice()
  max_units = bank/latest_price
  
  executeTrade(type='call', lots=int(buy_call_ratio*max_units))
  executeTrade(type='put', lots=int(max_units-int(buy_call_ratio*max_units)))

def predictType():
      # Simple Moving Average strategy
    price_current = getPrice()
    price_future = getPrice().shift(-1)

    class_positive = 1
    class_negative = 0
        
    np.seterr(divide = 'ignore')
    prediction = np.where(price_future > price_current, class_positive, class_negative)

    if prediction == 1:
        return 'put'
    else:
        return 'call'


def executeTrade(type_, lots):
  buy(ttype=type_, horizon='15', lots=lots)
  pass

def make_trade():
  global bank
  bank = getBank()

  latest_price = getPrice()
  max_units = bank/latest_price
  type = predictType()
  executeTrade(type=type, lots=int(buy_call_ratio*max_units))
  executeTrade(type='call' if type == 'put' else 'put', lots=max_units-int(buy_call_ratio*max_units))

def predict(model):
  auto("in.csv", f"{team}/{model}", "{pw}")

if __name__ == "__main__":
    import datetime

    first_trade = True
    while datetime.datetime.now() > datetime.datetime(year=2021, month=8, day=3, hour=21, minute=0):
        if first_trade:
            print('make first trade')
            bank = make_first_trade()
            first_trade = False


