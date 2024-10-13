from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
import json
import pandas as pd
import yfinance as yf

app = Flask(__name__)
CORS(app)

csv_list = 'nyse_stocks.csv'

#Number Reference for parameter inputs
numsReference = {
      "0": 0, "1": 1, "2": 2,"3": 3, "10": 10, "50": 50, "100": 100, "150": 150,
      "200": 200,
      "50mln":50000000, "200mln": 200000000, "10bln": 10000000000, "200bln": 200000000000
}

#POST request from front-end
@app.route("/data", methods=['POST'])
def receiveData():
      data = request.data
      data = json.loads(data)

      stocks = readStockList() #array of all stocks listed on csv
      validStocks = []         #result array of screened stocks

      #for curIndex in range(len(stocks)):
      for curIndex in range(0, 500, 1):                #TESTER                                     
            current = yf.Ticker(stocks[curIndex])
            
            try:
                  print(current.balance_sheet)
                  pass
            except: 
                  print("Did not work")
                  pass

            if(screenSector(data, stocks[curIndex]) == False): continue 
            if(screenCountry(data, stocks[curIndex]) == False): continue
            #if(screenPrice(data, current) == False): continue
            #if(screenYrChange(data, current) == False): continue
            
            validStocks += [stocks[curIndex]]

      if(len(validStocks)==0): validStocks = ["No Results"]
      return validStocks

def screenSector(data, ticker):
      try:
            industryInput = data['filterStates']['sector']['current']
            df = pd.read_csv(csv_list, usecols=['Symbol', 'Sector'])
            df.set_index('Symbol', inplace=True)
            if(industryInput != df['Sector'][ticker]):
                  return False
            return True
      except: return False     #catches API error

def screenCountry(data, ticker):
      try:
            countryInput = data['filterStates']['country']['current']
            df = pd.read_csv(csv_list, usecols=['Symbol', 'Country'])
            df.set_index('Symbol', inplace=True)
            if(countryInput != df['Country'][ticker]):
                  return False
            return True
      except: return False     #catches API error

def screenPrice(data, current):
      try:
            priceInput = data['filterStates']['price']['current']
            if(priceInput != 'Any'):
                  if priceInput[1: len(priceInput)] in numsReference.keys():         #Check if input value exists in numbers reference dictionary
                        dictValue = numsReference[priceInput[1: len(priceInput)]]    #Assigns corresponding number in dictionary to dictValue
                        lastPrice = current.fast_info.last_price
                        if(priceInput[0: 1] == "o"):                                 #checks if user selected "over"
                              if(dictValue >= lastPrice):
                                    return False                                     #if last price of the stock being checked is under parameter, skip this iteration of for loop
                        elif(priceInput[0: 1] == "u"):                               #checks if user selected "under"                                  
                              if(dictValue <= lastPrice):
                                    return False                                     #if last price of the stock being checked is over parameter, skip this iteration of for loop
            return True
      except: return False                                                           #catches API Error

def screenMktCap(data, current):
      try:
            mktCapInput = data['filterStates']['marketCap']['current']
            if(mktCapInput != "Any"):
                  if mktCapInput[1: len(mktCapInput)] in numsReference.keys():         #Check if input value exists in numbers reference dictionary
                        dictValue = numsReference[mktCapInput[1: len(mktCapInput)]]    #Assigns corresponding number in dictionary to dictValue
                        mktCap = current.fast_info.marketCap
                        if(mktCapInput[0: 1] == "o"):                                 #checks if user selected "over"
                              if(dictValue >= mktCap):
                                    return False                                     #if last price of the stock being checked is under parameter, skip this iteration of for loop
                        elif(mktCapInput[0: 1] == "u"):                               #checks if user selected "under"                                  
                              if(dictValue <= mktCap):
                                    return False           
            return True
      except: return False

def screenYrChange(data, current):
      try:
            yrChangeInput = data['filterStates']['yrChange']['current']
            yrChange = current.fast_info.year_change
            if(yrChangeInput != "Any"):
                  if(yrChangeInput == "up"):
                        if(yrChange <= 0): return False
                  elif(yrChangeInput == "down"):
                        if(yrChange >= 0): return False
            return True
      except: return False

'''
def screenVolume(data, current):
      try:
            volumeInput = data['filterStates']['volume']['current']
            if(volumeInput != "Any"):
                  if volumeInput[1: len(volumeInput)] in numsReference.keys():         #Check if input value exists in numbers reference dictionary
                        dictValue = numsReference[volumeInput[1: len(volumeInput)]]    #Assigns corresponding number in dictionary to dictValue
                        mktCap = current.fast_info.marketCap
                        if(volumeInput[0: 1] == "o"):                                 #checks if user selected "over"
                              if(dictValue >= mktCap):
                                    return False                                     #if last price of the stock being checked is under parameter, skip this iteration of for loop
                        elif(volumeInput[0: 1] == "u"):                               #checks if user selected "under"                                  
                              if(dictValue <= mktCap):
                                    return False           
            return True
      except: return False
'''

#read CSV from NASDAQ and add to an array
def readStockList():
      stocks = []
      df = pd.read_csv(csv_list)   
      rowCount = len(df)
      for i in range(rowCount):
            stocks += [df['Symbol'][i]]
      return stocks

if __name__ == "__main__":
      app.run(debug=True, port = 3001)
