import numpy as np      #NumPy for speedy and convenietn calculations
import requests as req  #This is the HTTP request library, to interact with exchange APIs
import datetime

import exchanges #this is where the data for exchange api core urls is kept adn similar stuff


def get_ohlc(pair,interval,since):
    '''This fucntion fetches historical OHLC(open low high close - prices) data from
       Kraken's API. The API returns data in JSON, which is decoded by Requests'
       own JSON decoder into dictionary format. The sequence of prices is then extracted 
       so that each element of the data list, is a row of values for a given time-point:
       data[i] = [time, open, high, low, close, volume-weighted average, volume, count]
       (idk what count does)
       The data is returned paired together with the API request parameters that were used to
       fetch it if it needs to ever be identified later.
       
       XXX This function has not yet got any real error handling, which is an issue since the HTTP request
       may easily fail for a number of reasons: 1. No internet. 2.Errors in HTTP 3. API errors due to 
       incorrect parameters being submitted... etc. etc.
	   
	   XXX This function has been hard-coded for connecting to Kraken's API only, this needs to be changed.
	   '''
    param = [pair,interval,since] #this is the parameters sent to request, stored to label the received data for further processing steps
    print("Requesting OHLC for:  "+str(param))
    r = req.get(exchanges.kraken_url+"public/OHLC",params={"pair":pair,"interval":interval,"since":int(since)})
    print("Response received for:  " + str(param)+". Status Code:  "+str(r.status_code))
    data = r.json()
    print("Data decoded from JSON for:  " +str(param))
    data = [data["result"][paircode(pair)], param]
    return data # the returned data is coupled to parameters to identify it if needed

def paircode(pair):
    '''Changes a standard pair eg. LTCUSD into the weird pair in Kraken JSON response, XLTCZUSD
    
    For some reason the API takes as input normal 3+3 letter currency pairs, e.g. LTCUSD is Litecoin-Dollar,
    but the JSON response containing the OHLC data adds an X in front of the first currency and a Z in front
    of the second(e.g. LTCUSD => XLTCZUSD), so to access the JSON results we need this.
    '''
    if(len(pair) !=6):
        #*** XXX some error handling/input validation needs to be done if input is not a 6 letter code a
        print("Pair names must be 6 letters long")
    return "X"+pair[0:3]+"Z"+pair[3:]

def convert_to_tohlcwv(data):#this function converts the array of historical values from kraken into an easily plotable array, as an np.array: [[T],[O],[H],[L],[C],[VWA],[V],[count]]
    '''This function converts the returned Kraken Data from get_ohcl into a
    format that is easier to plot. Instead of having a list of rows, so that to access the time we can do data["time"/0][i]
    instead of data[i][time]. This means we can plot it easily using matplotlib, and it is easier for calculation of
    moving averages of prices. data[0][0] is the time array.
    '''
    tohclwv_to_be = []
    for i in range(len(data[0][0])):
        tohclwv_to_be.append(np.array([np.float(row[i]) for row in data[0]]))#extracts the ith variable from each row, 
                                                                             #to make an array of just the ith variable
    tohlcwv = np.array(tohclwv_to_be)#convert to numpy array for speed and convenience
    return [tohlcwv,data[1]]#the returned data is coupled to the parameters in the second element, for identification, like in get_ohlc()

def sma_n(data, window=7):
    '''Calculates the simple moving average of the given time series
    
    For the first few elements the average is just the best it can do ie, 
    the 2-point, 3 point ... etc averages until its gone far enough. This is so that the SMA 
    array is the same length as the original array, for plotting against time nicely.
	
	The moving average is such that at index i of the data array, the moving average is the average of the last window elements, NOT
	the last window/2 and next window/2!
    '''
    sma_memory = [] #this is where the last n numbers are stored
    sma = np.empty_like(data) #returned array of mopvig averages
    for (i,item) in enumerate(data):
		if (len(sma_memory)>window):
			print("An error computing SMA in sma_n function, the memory array is longer than prescribed window size")#A small error-detecting code
        if (len(sma_memory) < window):#for the first few entries, the moving average is just the average of all preceding entries
            sma_memory.append(float(item))
            current = np.sum(sma_memory) / len(sma_memory)
            sma[i] = current
        else:
            sma_memory.pop(0)
            sma_memory.append(float(item))
            current = sum(sma_memory) / len(sma_memory)
            sma[i] = current
    return sma

#XXX this is in no way a complete class, it is in the making, not used in any other part of the program, just put here to get the ball rolling
class Market:
	'''The standard way of storing and handling historical data fetched from exchange APIs. A fetch function should grab data and return 
	   a Market object
	   '''
	
	
	def __init__(self, time, open, high, low, close, vwa, pair, exchange):
		
		self.pair = pair
		self.exchange = exchange
		

pass







