from psaw import PushshiftAPI
import datetime as dt
import config
import alpaca_trade_api as tradeapi
import yfinance as yf
import sys
import io
from collections import Counter
import re

# For encoding and decoding of special characters in the reddit posts.
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

# Instantiating the Alpaca API.
alpaca_api = tradeapi.REST(config.API_KEY,
                    config.API_SECRET,
                    base_url = config.API_URL)

assets = alpaca_api.list_assets()

# Selecting the stock symbol.
symbols = []
for asset in assets:
    symbols.append('$' + asset.symbol)

# Instatiating the Rddit API.
reddit_api = PushshiftAPI()

# Setting the start and end date.
""" End date """
end = dt.date.today()
end_month = int(end.strftime("%#m")) # Removing leading 0.
end_day = int(end.strftime("%#d")) # Removing leading 0.
""" Start date """
start = end - dt.timedelta(days = 7)
start_month = int(start.strftime("%#m")) # Removing leading 0.
start_day = int(start.strftime("%#d")) # Removing leading 0.

# Converting to Unix timestamp.
start_date = int(dt.datetime(start.year, start_month, start_day).timestamp())
end_date = int(dt.datetime(end.year, end_month, end_day).timestamp())

# Getting the title of all posts made on wallstreetbets subreddit.
submissions = list(reddit_api.search_submissions(before = end_date,
                                                after = start_date,
                                                subreddit = 'wallstreetbets',
                                                filter = ['title']))

# Getting all the stocks mentioned in the subreddit.
mentions = []
for submission in submissions :
    words = submission.title.split()
    for word in words :
        if word in symbols :
            mentions.append(word)

# Storing the count of mentions of each stock.
count = dict(Counter(mentions))
count_sorted = sorted(count.items(), key = lambda kv: kv[1], reverse=True)

""" # Most mentioned stock.
most_mentioned = max(count, key = count.get)
print(most_mentioned) """

""" Atleast 1-2 years of daily stock price data would be preferrablae for training the model.
    There may be stocks which do not have much data because of going public recently.
    Therefore, for the purpose of this project, prediction will be done on the most mentioned stock with atleast 365 rows of data. """

# Getting the stock data from Yahoo Finance.
for i in range(len(count_sorted)):
    
    ticker = yf.Ticker(count_sorted[i][0][1:]) # Excluding $ in the stock symbol.
    hist = ticker.history(period = "2y") # Data of past past two years.
    hist['Stock'] = count_sorted[i][0][1:] # Adding the stock symbol to the data.
    hist = hist[['Stock', 'Open', 'High', 'Low', 'Close', 'Volume']] # Rearranging the columns.

    if len(hist) >= 365 :
        break # Exit the loop if we have atleast 365 days of data.
    
hist.to_csv('Stock_data.csv') # Exporting the data to a csv.

