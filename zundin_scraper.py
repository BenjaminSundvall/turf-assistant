import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

class ZundinScraper:
    BASE_URL = "https://frut.zundin.se/zone.php?"
    ZUNDIN_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        pass

    def get_visits_data(self, zone_name, round_id):
        """Fetch historical visit data for a specific zone by its name and round ID"""
        filename = f"visits_data/{zone_name}_{round_id}.csv"

        # Check for cached data
        if os.path.exists(filename):
            print(f"{filename} already exists. Loading from file.")
            df = pd.read_csv(filename)
            return df

        # Scrape data from zundin
        print(f"{filename} not found. Scraping from zundin.")
        url = f"{self.BASE_URL}zonename={zone_name}&roundid={round_id}"
        response = requests.get(url)
        if response.status_code == 200:
            df = self.parse_visits_data(response.text, round_id)
            self.save_to_csv(df, filename)
            return df
        else:
            print(f"Error fetching data for zone {zone_name}: {response.status_code}")
            return None

    def parse_visits_data(self, html, round_id):
        """Parse historical visit data from HTML"""
        visits = []
        soup = BeautifulSoup(html, 'html.parser')

        if not soup.find(id='roundTakeovers'):
            print("No visit data found.")
            return None

        table = soup.find(id='roundTakeovers').find('table')  # Assuming the data is in a table
        for tr in table.select('tr')[1:-1]:
            visit = {}

            visit['user'] = tr.select('td')[0].text.strip()
            visit['points'] = int(tr.select('td')[1].text.strip())
            visit['hold_time'] = self.parse_hold_time(tr.select('td')[2].text.strip())
            visit['visit_date'] = tr.select('td')[3].select('script')[0].text.strip()[29:-4]

            visits.append(visit)

        # Add neutral visit at the beginning of round
        neutral_visit = {'user': 'neutral',
                         'points': 0,
                         'hold_time': 0,
                         'visit_date': datetime.now().strftime(self.ZUNDIN_TIME_FORMAT)}

        return pd.DataFrame(visits)

    def parse_hold_time(self, hold_time_str):
        """Parse hold time in format '1 days 13:37' to seconds"""
        if not hold_time_str:
            return 0

        split_str = hold_time_str.split(' days ')
        days = 0
        time = 0
        if len(split_str) == 1:
            time = split_str[0]
        elif len(split_str) == 2:
            days = split_str[0]
            time = split_str[1]
        hours, minutes, seconds = time.split(':')
        return 24*3600*int(days) + 3600*int(hours) + 60*int(minutes) + int(seconds)

    def save_to_csv(self, df, filename):
        """Save historical data to a CSV file"""
        df.to_csv(filename, index=False)
        print(f"  {filename} saved successfully.")
