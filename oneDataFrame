import pandas as pd
from collections import Counter
lowStats = ['P/B', 'Inst Own', 'Float Short', 'Debt/Eq', 'RSI']

def getAllAverages(df):
    averages = {}
    for stat in df.columns.values[2:]:
        list = df[stat].apply(lambda x: float(str(x)[:-1])).tolist()
        averages[stat] = round(sum(list)/len(list), 2)
    return averages

def getSectorAverages(df):
    averages = {}
    for sector in dict.fromkeys(df['Sector'].tolist()).keys():
        averages[sector] = {}
        sectorDF = df[df['Sector'] == sector]
        for stat in df.columns.values[2:]:
            list = sectorDF[stat].apply(lambda x: float(str(x)[:-1])).tolist()
            averages[sector][stat] = round(sum(list)/max(len(list), 1), 2)
    return averages

def getAboveAverageSectors(df):
    goodSectors = {}
    averages = getAllAverages(df)
    sectorAverages = getSectorAverages(df)
    for stat in df.columns.values[2:]:
        sects = []
        for sector in dict.fromkeys(df['Sector'].tolist()).keys():
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
    for sector in dict.fromkeys(df['Sector'].tolist()).keys():
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
    while len(goodStocks) > 20:
        list = goodStocks.tolist()
        average = round(sum(list)/len(list), 2)
        goodStocks = goodStocks[goodStocks >= average]
    goods = []
    for i in goodStocks.index:
        goods.append(df.loc[i]['Ticker'])
    return goods

def getBestStocks(df):
    bests = []
    for stat in df.columns.values[2:]:
        bests+=getStocksWithBest(stat, df)
    return Counter(bests)

df = pd.read_csv('0.csv')

tt = scoreSectors(df)
for t in tt:
    print(t, ':', len(tt[t]))

print(getBestStocks(df))
