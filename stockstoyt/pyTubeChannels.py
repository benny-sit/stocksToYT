from pytube import Search
import yfinance as yf
yf.set_tz_cache_location("yf/cache/")
from constants import STOCKS, CHANNEL_ID
import re
import requests
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from requests_cache import CacheMixin, SQLiteCache
from pyrate_limiter import Duration, RequestRate, Limiter
from web_screenshot import screenshot_youtube_channels
class CachedLimiterSession(CacheMixin, LimiterMixin, requests.Session):
    pass

session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yf/yfinance.cache"),
)


ALL_STOCKS = [s for l in STOCKS.values() for s in l]

def get_stock_info(stocks):
  stocks_info = yf.Tickers(' '.join(stocks), session=session)
  yahoo_info = {}
  for k in stocks_info.tickers.keys():
    print("GETTING ASSET DATA: " + k )
    yahoo_info[k] = stocks_info.tickers[k].info
  return yahoo_info


def get_youtube_videos_of_stock_companies(stocks_names):
  res_videos = {}
  for symbol, short_name in stocks_names.items():
    s = Search(short_name)
    selected_video = None
    is_author_verified = False
    for v in s.results:
      if v.author == short_name:
        selected_video = v
        is_author_verified = True
        break
    else:
      selected_video = s.results[0]
      
    res_videos[symbol] = { k: selected_video[k] for k in ['channel_id', 'watch_url', 'views', 'title']}
    res_videos[symbol].is_verified= is_author_verified
    
  return res_videos
    

def get_handle_video_channel_id(channel_name):
  url = f'https://yt.lemnoslife.com/channels?handle=@{channel_name}'
  r = requests.get(url)
  data = r.json()

  if 'items' in data and data['items'] and 'id' in data['items'][0]:
    print(data['items'][0], 'ITEMS', data['items'][0]['id'])
    return data['items'][0]['id']
  

def get_channel_ids(stocks_names):
  res_channel_ids = {}
  for symbol, short_name in stocks_names.items():
    c_id =get_handle_video_channel_id(short_name)
    if not c_id:
      c_id = get_handle_video_channel_id(short_name.split(' ')[0])
    
    res_channel_ids[symbol] = c_id

  return res_channel_ids


def run():
  info = get_stock_info(ALL_STOCKS)
  stock_short_name = {k: re.sub('[^A-Za-z0-9. ]','',v['shortName']).replace('  ', ' ') for k, v in info.items() if 'shortName' in v}
  stock_websites = {k: v['website'] for k, v in info.items() if 'website' in v}

  # stock_channel_ids = get_channel_ids(stock_short_name)
  screenshot_youtube_channels(CHANNEL_ID, stock_short_name)
  
  # stocks_channel_ids = get_youtube_videos_of_stock_companies(stock_short_name)
  
  
  # print("END",stock_channel_ids)