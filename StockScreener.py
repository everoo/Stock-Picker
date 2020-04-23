import requests
import pandas as pd
import itertools
import numpy as np
from sklearn.neural_network import MLPRegressor

sectors = ['Utilities', 'Technology', 'Industrial Goods', 'Healthcare', 'Financial', 'Consumer Goods', 'Conglomerates', 'Basic Materials', 'Services']
stats = ['P/B', 'Inst Own', 'Float Short', 'ROE', 'Curr R', 'Debt/Eq', 'RSI', 'Gap', 'Rel Volume', 'Change', 'Perf Week', 'Perf Month', 'Perf Year', 'Volatility W', 'Volatility M', 'SMA20', 'SMA50', 'SMA200']
lowStats = ['P/B', 'Inst Own', 'Float Short', 'Debt/Eq', 'RSI']

def getDailyStocks(day):
    url = 'https://finviz.com/screener.ashx?v=152&f=sh_curvol_o50,sh_price_u5&c=1,3,6,11,28,30,33,35,38,42,43,46,50,51,52,53,54,59,61,64,65,66,67'
    df_list = pd.read_html(requests.get(url).content)
    total = int(df_list[-3][0][0][7:-3])
    df = df_list[-2]
    for i in range(int(total/20)):
        print(i)
        df = df.append(pd.read_html(requests.get(url+('&r='+str(20*(i+1)+1))).content)[-2][1:])
    df = df.rename(columns=df.loc[0])[1:]
    replacements = {'Perf Year': '0.00%', 'Perf Month': '0.00%', 'Perf Week': '0.00%', 'Debt/Eq': '0.30', 'Curr R': '2.00', 'ROE': '0.00%', 'Float Short': '0.00%', 'Inst Own': '0.00%', 'P/B': '3.00', 'Market Cap': '300000', 'Volatility W':'0.00%', 'Volatility M':'0.00%', 'SMA20':'0.00%', 'SMA50':'0.00%', 'SMA200':'0.00%', 'Change':'0.00%', 'RSI':'50.00', 'Gap':'0.00%', 'Rel Volume':'0.00'}
    for replacement in replacements:
        df[replacement] = df[replacement].replace('-', replacements[replacement])
    df.to_csv(day+'.csv', index=False, encoding='utf-8')

def getAllAverages(df):
    averages = {}
    for stat in stats:
        list = df[stat].apply(lambda x: float(str(x)[:-1])).tolist()
        averages[stat] = round(sum(list)/len(list), 2)
    return averages

def getSectorAverages(df):
    averages = {}
    for sector in sectors:
        averages[sector] = {}
        sectorDF = df[df['Sector'] == sector]
        for stat in stats:
            list = sectorDF[stat].apply(lambda x: float(str(x)[:-1])).tolist()
            averages[sector][stat] = round(sum(list)/len(list), 2)
    return averages
    
def getAboveAverageSectors(df):
    goodSectors = {}
    averages = getAllAverages(df)
    sectorAverages = getSectorAverages(df)
    for stat in stats:
        sects = []
        for sector in sectors:
            if stat in lowStats:
                if sectorAverages[sector][stat] < averages[stat]:
                    sects.append(sector)
            else:
                if sectorAverages[sector][stat] > averages[stat]:
                    sects.append(sector)
        goodSectors[stat] = sects
    return goodSectors
        
def scoreSectors(df):
    goodSectors = getAboveAverageSectors(df)
    scores = {}
    for sector in sectors:
        scores[sector] = []
        for k, v in goodSectors.items():
            if sector in v:
                scores[sector].append(k)
    return scores

def getStocksWithBest(stat, df):
    averages = getAllAverages(df)
    average = averages[stat]
    goodStocks = df[stat].apply(lambda x: float(str(x)[:-1]))
    if stat in lowStats:
        goodStocks = goodStocks[goodStocks <= average]
    else:
        goodStocks = goodStocks[goodStocks >= average]
#    while len(goodStocks) > 20:
#        list = goodStocks.tolist()
#        average = round(sum(list)/len(list), 2)
#        goodStocks = goodStocks[goodStocks >= average]
    goods = []
    for i in goodStocks.index:
        goods.append(df.loc[i]['Ticker'])
    return goods

def findVolumeTrends(startDay, count, cutOff):
    types = list(itertools.product('GL', repeat=count))
    counts = list(itertools.product('10', repeat=count))
    which = {}
    all = {}
    for n, GL in enumerate([''.join(t) for t in types]):
        which[GL] = list([int(i) for i in counts[n]])
        all[GL] = []
    dailyDfs = {}
    for i in range(count):
        dailyDfs[startDay-count+i+1] = pd.read_csv(str(startDay-count+i+1)+'.csv', index_col='Ticker')
    for ticker in dailyDfs[startDay].index:
        listt = [2 for _ in range(count)]
        for day in dailyDfs:
            if ticker in dailyDfs[day].index:
                per = float(dailyDfs[day].loc[ticker]['Rel Volume'])
                if per > 1:
                    listt[day-(startDay-count+1)] = 1
                elif per < 1:
                    listt[day-(startDay-count+1)] = 0
        print(listt)
        for k, v in which.items():
            if listt == v:
                all[k].append(ticker)
    return all
    
def findGLTrends(startDay, count, cutOff):
    types = list(itertools.product('GL', repeat=count))
    counts = list(itertools.product('10', repeat=count))
    which = {}
    all = {}
    for n, GL in enumerate([''.join(t) for t in types]):
        which[GL] = list([int(i) for i in counts[n]])
        all[GL] = []
    dailyDfs = {}
    for i in range(count):
        dailyDfs[startDay-count+i+1] = pd.read_csv(str(startDay-count+i+1)+'.csv', index_col='Ticker')
    for ticker in dailyDfs[startDay].index:
        listt = [2 for _ in range(count)]
        for day in dailyDfs:
            if ticker in dailyDfs[day].index:
                per = float(dailyDfs[day].loc[ticker]['Change'][:-1])
                if per > cutOff:
                    listt[day-(startDay-count+1)] = 1
                elif per < -cutOff:
                    listt[day-(startDay-count+1)] = 0
        for k, v in which.items():
            if listt == v:
                all[k].append(ticker)
    return all

def getTopNStocks(df, n):
    goodStocks = []
    for stat in stats:
        goodStocks += getStocksWithBest(stat, df)
    seen = {}
    for stock in goodStocks:
        if stock in seen:
            seen[stock] += 1
        else:
            seen[stock] = 1
    d_view = [ (v,k) for k,v in seen.items() ]
    d_view.sort(reverse=True)
    returning = {}
    for v,k in d_view[:n]:
        returning[k] = v
    return returning
    
#def getAIlayout(startDay, count):
#    dailyDfs = {}
#    for i in range(count):
#        dailyDfs[startDay-count+i+1] = pd.read_csv(str(startDay-count+i+1)+'.csv', index_col='Ticker')
#    data = []
#    target = []
#    for ticker in dailyDfs[startDay].index:
#        tmp = []
#        including = True
#        for i in range(count-1):
#            if ticker in dailyDfs[startDay-i-1].index:
#                if i == 0:
#                    tmp = tmp + dailyDfs[startDay-i-1].loc[ticker].values.tolist()[1:]
#                else:
#                    tmp = tmp + dailyDfs[startDay-i-1].loc[ticker].values.tolist()[13:]
#            else:
#                including = False
#        if including:
#            data.append(tmp)
#            target.append(float(dailyDfs[startDay].loc[ticker]['Change'][:-1]))
#    y=np.array([np.array([float(str(t)[:-1]) for t in xi]) for xi in data])
#    return [y, np.array(target)]
#
#
#def learn(data, target):
#    clf = MLPRegressor(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
#    clf.fit(data, target)
#    print(data[0])
#    print(clf.predict(data[0]))
    
#getDailyStocks('3')

for k, v in findVolumeTrends(3, 3, 50).items():
    if not v == []:
        print(k, ':', v)
#for k, v in scoreSectors(pd.read_csv('2.csv')).items():
#    print(k, len(v))

#df = pd.read_csv('2.csv')
#print(getTopNStocks(df[df['Sector'] == 'Technology'], 10))

#print(getTopNStocks(df, 10))

##getDailyStocks('3')
#xy = getAIlayout(3, 3)
##print(xy[0][0])
#learn(xy[0], xy[1])
