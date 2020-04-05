import sklearn
from quantopian.pipeline.data import USEquityPricing, Fundamentals
from quantopian.pipeline.data.sentdex import sentiment as news
from quantopian.pipeline.data.psychsignal import aggregated_twitter_withretweets_stocktwits as media
from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output

# Part One: Sorting
# 1. Find news and social media(hype) of sectors
#     - Find hype value of every stock in a sector
#     - Get the average hype of each sector
#     - Find stock in each sector with good hype
#     - Good hype means its discussed x times more than the average sector hype
# DONE in sector_filter_pipeline() pipe named 'sectorFilter'
# 2. Create good fundamentals filter

# Part Two: Create Buying AI
# 1. Initialize multiple AI
#     - Have an AI for less than 0.50
#     - Have an AI for between 0.50 and 10.00
#     - Have an AI for between 10.00 and 50.00
#     - HAve an AI for above 50.00

# Part Three: Create Picking AI
# 1. Have an AI for popular sectors

# Part Four: Creat an AI that changes the base pipeline values and checks if that improves algo

#numbers to sectors           4/03 
#101 - Basic Materials         14
#102 - Consumer Cyclical       29
#103 - Financial Services      20
#104 - Real Estate             8
#205 - Consumer Defensive      25
#206 - Healthcare              25
#207 - Utilities               9
#308 - Communication Services  19
#309 - Energy                  24
#310 - Industrials             21
#311 - Technology              29

def initialize(context):
    context.sectorCount = {101: 0, 102: 0, 103: 0, 104: 0, 205: 0, 206: 0, 207: 0, 308: 0, 309: 0, 310: 0, 311: 0}
    attach_pipeline(sector_hype_pipeline(), 'sectorFilter')
    
def before_trading_start(context, data):
    context.pipe = pipeline_output('sectorFilter')
    for sector in context.pipe['Sector']:
        if sector in context.sectorCount.keys():
            context.sectorCount[sector] += 1
    print(context.sectorCount)
    print(len(context.pipe))
    print(context.pipe)
    
def sector_hype_pipeline():
    newsRating = news.sentiment_signal.latest
    mediaCount = media.bear_scored_messages.latest + media.bull_scored_messages
    mediaRating = media.bull_minus_bear.latest
    rating = (newsRating>4) | ((mediaRating>2) & (mediaCount>10)) | (((mediaRating>1) & (mediaCount>5)) & (newsRating>0)) | ((mediaRating>0) & (newsRating>2))
        
    return Pipeline(
        columns={
            'Media Count': mediaCount,
            'Media Rating': mediaRating,
            'News Rating': newsRating,
            'Sector': Fundamentals.morningstar_sector_code.latest,
        },
        screen = rating
    )
