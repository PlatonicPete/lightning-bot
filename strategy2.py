import lightningbot as lb

import numpy as np
import matplotlib.pyplot as plt
import datetime
#A "mean reversion" strategy, which can be tested for different timescales, and different currencies



def mean_reversion(prices, long_window, short_window, initial_investment,reverse=False,verbose=False):
	'''
	Takes in simple close price data, two windows for SMAs, an initial investment and outputs a set of arrays representing the time
	evolution of
	holdings in crypto, fiat holdings, value of holdings and a bunch of other stuff.
	
	reverse argument means that if true, the algo does the opposite of what it normally would do.
	'''
	long = np.empty_like(prices)
	short = np.empty_like(prices)
	long_mem = []
	short_mem = []
	holdings = np.zeros_like(prices)
	value = np.zeros_like(prices)
	fiat = np.zeros_like(prices)
	inout = False
	
	value[0] = initial_investment
	fiat[0] = initial_investment
	
	for (i,price) in enumerate(prices):
		
		#calculate SMAs
		if (len(long_mem) == long_window):
			long_mem.pop(0)#remove first element, but only if we have reached full window size
		long_mem.append(price)
		long[i] = np.sum(long_mem)/len(long_mem)
		
		if (len(short_mem) == short_window):
			short_mem.pop(0)#remove first element, but only if we have reached full window size
		short_mem.append(price)
		short[i] = np.sum(short_mem)/len(short_mem)
		
		#decide whether to buy or sell or do nothing and change holdings accordingly
		
		if(i==0): 
			continue #can't reach i-1 index correctly
		
		if(reverse==False):
			if(((short[i] > long[i]) and (short[i-1] < long[i-1])) and inout==True):#UP crossing, sell
				fiat[i] = price*holdings[i-1]
				holdings[i] = 0
				inout = False
				if(verbose==True):
					print("Sold@"+str(price))
			elif(((short[i] < long[i])and(short[i-1] > long[i-1])) and inout==False):#DOWN crossing, buy
				holdings[i] = fiat[i-1]/price
				fiat[i] = 0
				inout = True
				if(verbose==True):
					print("Bought@"+str(price))
			else:#no change, still update fiat and holdings
				holdings[i] = holdings[i-1]
				fiat[i] = fiat[i-1]
		else:#the reversed algorithm does opposite of what the otherone would have done
			if(((short[i] < long[i]) and (short[i-1] > long[i-1])) and inout==True):#UP crossing, sell
				fiat[i] = price*holdings[i-1]
				holdings[i] = 0
				inout = False
				if(verbose==True):
					print("Sold@"+str(price))
			elif(((short[i] > long[i])and(short[i-1] < long[i-1])) and inout==False):#DOWN crossing, buy
				holdings[i] = fiat[i-1]/price
				fiat[i] = 0
				inout = True
				if(verbose==True):
					print("Bought@"+str(price))
			else:#no change, still update fiat and holdings
				holdings[i] = holdings[i-1]
				fiat[i] = fiat[i-1]
		#calculate value
		value[i] = fiat[i] + holdings[i]*price
		if value[i]<0:
			print("BUST!!!")
			break
		
		#print(value[i])
		#print(fiat[i])
		#print(holdings[i])
	
	final_profit_percentage = value[-1]/value[0] - 1.0
	final_gain = value[-1] - value[0]
	
	return (price,long,short,value,holdings,fiat,final_profit_percentage,final_gain)

#bitcoin = lb.get_ohlc("XBTUSD",15,datetime.datetime(year=2018, month=1,day=2,hour=12).timestamp())
#btc = lb.convert_to_tohlcwv(bitcoin)
#print(btc)
#print(len(bitcoin))



#result = mean_reversion(btc[0][4],24,7,100.0)
#result2 = mean_reversion(btc[0][4],24,7,100.0,reverse=True)

#plt.plot(result[3],label='forward')
#plt.plot(result2[3],label='reverse')
#plt.legend()
#plt.savefig("XBTUSD-15min-24-4-value.png")
#plt.clear()

#plt.plot(btc[0][4])
#plt.savefig("XBTUSD-15min-24-4-price.png")
#plt.clear()
#print(result[6])
#print(result2[6])



def test_algo(interval,since,l,l_min=3,s_min=2,name="untitled",plots=False):
	#get data
	raw = lb.get_ohlc("XBTUSD",interval,since)
	data = lb.convert_to_tohlcwv(raw)
	max_profit = {'value':0,'params':[]}
	print(len(data[0][4]))
	#loop through varied params and run algo with each paramset, output plots for each run
	for i in range(l_min,l+1):
		for j in range(s_min,i):
			result = mean_reversion(data[0][4],i,j,100.0)
			result2 = mean_reversion(data[0][4],i,j,100.0,reverse=True)
			
			if(plots==True):
				plt.plot(result[3],label='forward')
				plt.plot(result2[3],label='reverse')
				plt.legend()
				plt.xlabel("Time")
				plt.ylabel("Value of investment")
				plt.title("XBTUSD trading algo with l="+str(i)+", s="+str(j)+"on interval "+str(interval)+"min")
				plt.savefig(str(name)+"XBTUSD-"+str(interval)+"min-L"+str(i)+"-S"+str(j)+"-value.png")
				plt.cla()
			if(result2[6]>max_profit['value']):
				max_profit['value']=result2[6]
				max_profit['params']=[interval,i,j,True]#params are interval, long, short, reverse or not
			
			if(result[6]>max_profit['value']):
				max_profit['value']=result[6]
				max_profit['params']=[interval,i,j,False]
			
			print("l="+str(i)+", s="+str(j)+", F="+str(result[6])+", R="+str(result2[6]))


	#plot the price
	if(plots!=False):
		plt.plot(data[0][1])
		plt.savefig(str(name)+"XBTUSD-15min-24-4-price.png")
	
	#output some rough benchmark numbers
	print(max_profit)

#test_algo(15,9,s_min=3)
test_algo(15,l=15,s_min=5,name="2k12",since=datetime.datetime(year=2018, month=1,day=2,hour=12).timestamp(),plots="something")