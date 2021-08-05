# competition rule
# price = open price
# every minute, 1 lot, horizon = 15,30,60 min
# earn price difference between buy and execute price
# call option, expect price increase
# put options, expect price decrease

# to maximize, determine best horizon and option type every minute
import requests
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
  pass

def make_first_trade():
  test()
  latest_price = getPrice()
  max_units = bank/latest_price
  executeTrade(type=type, lots=int(buy_call_ratio*max_units))
  executeTrade(type='call' if type == 'put' else 'put', lots=max_units-int(buy_call_ratio*max_units))

def predictType():
  pass

def executeTrade(type, lots):
  pass

def make_trade():
  global bank
  bank = getBank()

  latest_price = getPrice()
  max_units = bank/latest_price
  type = predictType()
  executeTrade(type=type, lots=int(buy_call_ratio*max_units))
  executeTrade(type='call' if type == 'put' else 'put', lots=max_units-int(buy_call_ratio*max_units))



if __name__ == "__main__":
    import datetime

    first_trade = True
    while datetime.datetime.now() > datetime.datetime(year=2021, month=8, day=3, hour=21, minute=0):
        if first_trade:
            print('make first trade')
            bank = make_first_trade()
            first_trade = False
        

