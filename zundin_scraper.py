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

    def get_takeover_data(self, zone_name, round_id):
        """Fetch historical takeover data for a specific zone by its name and round ID"""
        filename = f"takeover_data/{zone_name}_{round_id}.csv"

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
            df = self.parse_takeover_data(response.text, round_id)
            self.save_to_csv(df, filename)
            return df
        else:
            print(f"Error fetching data for zone {zone_name}: {response.status_code}")
            return None

    def parse_takeover_data(self, html, round_id):
        """Parse historical takeover data from HTML"""
        takeovers = []
        soup = BeautifulSoup(html, 'html.parser')

        if not soup.find(id='roundTakeovers'):
            print("No takeover data found.")
            return None

        table = soup.find(id='roundTakeovers').find('table')  # Assuming the data is in a table
        for tr in table.select('tr')[1:-1]:
            takeover = {}

            takeover['user'] = tr.select('td')[0].text.strip()
            takeover['points'] = tr.select('td')[1].text.strip()
            takeover['duration'] = tr.select('td')[2].text.strip()
            takeover['date'] = tr.select('td')[3].select('script')[0].text.strip()[29:-4]

            # dt = datetime.strptime(takeover['date'], self.ZUNDIN_TIME_FORMAT)

            takeovers.append(takeover)

        return pd.DataFrame(takeovers)

    def save_to_csv(self, df, filename):
        """Save historical data to a CSV file"""
        df.to_csv(filename, index=False)
        print(f"  {filename} saved successfully.")
