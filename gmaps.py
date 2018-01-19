import numpy as np      #NumPy for speedy and convenietn calculations
import requests as req  #This is the HTTP request library, to interact with exchange APIs
import datetime

import matplotlib.pyplot as plt

kraken_url = "https://api.kraken.com/0/"  #This is the base url of the API

def get_ohlc(pair,interval,since):
    '''This fucntion fetches historical OHLC(open low high close) data from
       Kraken's API. The API returns data in JSON, which is decoded by Requests'
       own JSON decoder into dictionary format. The data is then finally a list
       of rows of values arrange like this:
       data[i] = [time, open, high, low, close, volume-weighted average, volume, count]
       (idk what count does)'''
    param = [pair,interval,since] #this is used to label the received data for further processing steps
    print("Requesting OHLC for:  "+str(param))
    r = req.get(kraken_url+"public/OHLC",params={"pair":pair,"interval":interval,"since":int(since)})
    print("Response received for:  " + str(param)+". Status Code:  "+str(r.status_code))
    data = r.json()
    print("Data decoded from JSON for:  " +str(param))
    data = [data["result"][paircode(pair)], param]
    return data # the returned data is coupled to parameters to identify it if needed

def paircode(pair):
    '''Changes a standard pair eg. LTCUSD into the weird pair in Kraken JSON response, XLTCZUSD'''
    if(len(pair) !=6):
        #*** Throw error
        print("Pair names must be 6 letters long")
    return "X"+pair[0:3]+"Z"+pair[3:]

def convert_to_tohlcwv(data):#this function converts the array of historical values from krakeninto an easily plotable array, as an np.array: [[T],[O],[H],[L],[C],[VWA],[V],[count]]
    '''This function converts the returned Kraken Data from get_ohcl into a
    format that is easier to plot vs time: e.g.
    can plot tohlcwv[0] (time) vs tohlcwv[4] (close)
    '''
    tohclwv_to_be = []
    for i in range(len(data[0][0])):
        tohclwv_to_be.append(np.array([np.float(row[i]) for row in data[0]]))
    tohlcwv = np.array(tohclwv_to_be)
    return [tohlcwv,data[1]]#the returned data is coupled to the parameters in the second element

def sma_n(data, n=7):
    '''Calculates the simple moving average of the given time series'''
    sma_memory = [] #this is where the last n numbers are stored
    sma = np.empty_like(data) #returned array of mopvig averages
    for (i,item) in enumerate(data):
        if (len(sma_memory) < n):#for the first few times, the moving average is just the average of all preceding entries
            sma_memory.append(float(item))
            current = np.sum(sma_memory) / len(sma_memory)
            sma[i] = current
        else:
            sma_memory.pop(0)
            sma_memory.append(float(item))
            current = sum(sma_memory) / len(sma_memory)
            sma[i] = current
    return sma

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



def simple_tp(N):
    grand = np.float32(1.0)
    gand= [[1],[],[]]
    ns = []
    gs = []
    for n in range(1,N):
        p = sma_n(LTC15[0][4],n)
        bought = False
        print(n)
        for i in range(20, (len(p) - 1)):
            if (p[i] > p[i - 1]) and (p[i - 1] < p[i - 2]) and bought:  # sell condtion /\
                print("Sell@" + str(LTC15[0][1][i + 1]))
                grand *= LTC15[0][1][i + 1]
                gand[0].append(grand)
                gand[1].append(LTC15[0][1][i + 1])
            elif (p[i] < p[i - 1]) and (p[i - 1] > p[i - 2]):  # buy condition \/
                print("Buy@" + str(LTC15[0][1][i + 1]))
                grand /= LTC15[0][1][i + 1]
                gand.append(grand)
                gand[2].append(LTC15[0][1][i + 1])
                bought = True
        gs.append(grand)
        ns.append(n)
    print(gs)
    return (ns,gs)

def simple_tp_test(pair,interval,N,since,wich_indicate=4,wich_buy=1):
    recent = get_ohlc(pair, interval, since)
    data = convert_to_tohlcwv(recent)
    gains = np.ones(N,dtype=float)
    for n in range(1,N+1):
        p=sma_n(data[0][wich_indicate],n)
        bought = False

        #the buy and sell conditions themselves

        for i in range(n+1,len(p)-1):

            # sell condtion, a top reversal like this => /\
            if (p[i] < p[i - 1]) and (p[i - 1] > p[i - 2]) and bought:  # sell condtion /\
                gains[n - 1] *= data[0][wich_buy][i+1]
                bought=False
            elif (p[i] > p[i - 1]) and (p[i - 1] < p[i - 2]) and bought==False:
                gains[n - 1] /= data[0][wich_buy][i + 1]
                bought=True
    return(gains)

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



