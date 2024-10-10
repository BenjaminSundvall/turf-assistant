import requests
from datetime import datetime, timezone, timedelta
import urllib.parse
import time

TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def get_latest_takes(start_time):
    end_time = datetime.now(timezone.utc)
    print('Getting latest takes between', start_time, 'and', end_time)

    url_date = urllib.parse.quote_plus(start_time.strftime(TURF_TIME_FORMAT))
    url = 'https://api.turfgame.com/v4/feeds/takeover?afterDate=' + url_date
    takes = requests.get(url).json()

    return takes, end_time




start_time = datetime.now(timezone.utc) - timedelta(minutes=30)

takes, end_time = get_latest_takes(start_time)
time.sleep(20*60)
takes, end_time = get_latest_takes(end_time)