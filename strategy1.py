import lightningbot as lb
import datetime

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