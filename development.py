import numpy as np      #NumPy for speedy and convenietn calculations
import requests as req  #This is the HTTP request library, to interact with exchange APIs
import datetime

import matplotlib.pyplot as plt

kraken_url = "https://api.kraken.com/0/"  #This is the base url of the API
#The API has a public part, and a private part. Calls are limited, but shoudl not be an issue


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
       incorrect parameters being submitted... etc. etc.'''
    param = [pair,interval,since] #this is used to label the received data for further processing steps
    print("Requesting OHLC for:  "+str(param))
    r = req.get(kraken_url+"public/OHLC",params={"pair":pair,"interval":interval,"since":int(since)})
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
    moving averages of prices
    '''
    tohclwv_to_be = []
    for i in range(len(data[0][0])):
        tohclwv_to_be.append(np.array([np.float(row[i]) for row in data[0]]))#extracts the ith variable from each row, 
                                                                             #to make an array of just the ith variable
    tohlcwv = np.array(tohclwv_to_be)#convert to numpy array for speed and convenience
    return [tohlcwv,data[1]]#the returned data is coupled to the parameters in the second element, for identification, like in get_ohlc()

def sma_n(data, n=7):
    '''Calculates the simple moving average of the given time series
    
    For the first few elements the average is just the best it can do ie, 
    the 2-point, 3 point ... etc averages until its gone far enough. This is so that the SMA 
    array is the same length as the original array, for plotting against time nicely.
    '''
    sma_memory = [] #this is where the last n numbers are stored
    sma = np.empty_like(data) #returned array of mopvig averages
    for (i,item) in enumerate(data):
        if (len(sma_memory) < n):#for the first few entries, the moving average is just the average of all preceding entries
            sma_memory.append(float(item))
            current = np.sum(sma_memory) / len(sma_memory)
            sma[i] = current
        else:
            sma_memory.pop(0)
            sma_memory.append(float(item))
            current = sum(sma_memory) / len(sma_memory)
            sma[i] = current
    return sma


##The rest of the code is just me playing to see how I can use the above to test a trading strategy, and plotting some stuff

recent_LTC60 = get_ohlc("ETHUSD",60,datetime.datetime(year=2018, month=1,day=14,hour=12).timestamp())
recent_LTC15 = get_ohlc("ETHUSD",15,datetime.datetime(year=2018, month=1,day=14,hour=12).timestamp())
LTC15 = convert_to_tohlcwv(recent_LTC15)
LTC60 = convert_to_tohlcwv(recent_LTC60)
#print(LTC15[0])

#avg_close = np.sum(LTC[0][4])/len(LTC[0][4])
#avg_volume = np.sum(LTC[0][6])/len(LTC[0][6])
#d = 0.1
#f = d*avg_close/avg_volume
#plt.bar(LTC[0][0],f*LTC[0][6])
#plt.plot(LTC[0][0],LTC[0][4])
#plt.savefig("vol.png")

plt.plot(LTC15[0][0],LTC15[0][4],color=(0,0,0,0.2))
plt.plot(LTC15[0][0],sma_n(LTC15[0][4],7),color='r')
plt.plot(LTC15[0][0],sma_n(LTC15[0][4],11),color='g')
plt.plot(LTC15[0][0],sma_n(LTC15[0][4],16),color='k')
plt.savefig(str(datetime.datetime.now().timestamp())+".png")

def simple_tp_test(pair,interval,N,since,wich_indicate=4,wich_buy=1):
    '''This function fetches data from kraken about prices of a given pair with given interval
    then it tests a simple turning point strategy for moving averages from length 1 to N. 
    
    wich_indicate parameter decides which price(open/high/low/close) to use for SMA,
    wich_buy paramenter decides which price to use as the buy/sell price
    The default parameters are such that it uses the close price to decide, 
    and the open price of the next interval to buy
    
    The output is the gain in "x" (as in 2x means double your money, 3x tripe, 1.5x.. etc.etc)
    Mathematically it's gain = final_money/initial_money though, there is an expection, cause if there isn't
    a sell for every buy the gain may be weirdly low, like 1e-5. Normal values seem to be in the 0.7-1.4 range.
    
    it's a pretty bad strategy though, but there's lots of optimisations that could be put in:
    1. Currently it can only go long. It would be good if it could go short too.
    2. It needs to have a rule for deciding when it's shorting season and when it's buying season
    '''
    recent = get_ohlc(pair, interval, since)
    data = convert_to_tohlcwv(recent)
    gains = np.ones(N,dtype=float)
    for n in range(1,N+1):
        p=sma_n(data[0][wich_indicate],n)
        
        bought = False#this is used so that if you've bought, the next thing you'll do is sell and vice versa
        
        #the buy and sell conditions themselves
        for i in range(n+1,len(p)-1):

            # sell condtion, a top reversal like this => /\
            #i.e. if moving average reverses to turn downwards, sell(hence name of turning point(tp)) strategy)
            if (p[i] < p[i - 1]) and (p[i - 1] > p[i - 2]) and bought:  # sell condtion /\
                gains[n - 1] *= data[0][wich_buy][i+1]
                bought=False
            elif (p[i] > p[i - 1]) and (p[i - 1] < p[i - 2]) and bought==False:#This is the equivalent condition to buy
                gains[n - 1] /= data[0][wich_buy][i + 1]
                bought=True
    return(gains)#returns an array of gains for each value of N -> the length of the moving average


##This simply calculate
start = datetime.datetime(year=2018, month=1,day=2,hour=12).timestamp()
inter = 15
eth = simple_tp_test("ETHUSD",inter,15,start)
ltc = simple_tp_test("LTCUSD",inter,15,start)
xbt = simple_tp_test("XBTUSD",inter,15,start)
xrp = simple_tp_test("XRPUSD",inter,15,start)
print("ETH: " + str(eth))
print("LTC: " + str(ltc))
print("XBT: " + str(xbt))
print("XRP: " + str(xrp))



