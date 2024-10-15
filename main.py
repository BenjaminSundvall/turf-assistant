from datetime import datetime
import pandas as pd


from gui import FoliumGUI
from zonestats import ZoneStats
from turfclasses import Coordinate
from turfapi import TurfAPI
from zundin_scraper import ZundinScraper
from util import get_round_from_date


if __name__ == "__main__":
    # Ryd area
    northeast = Coordinate(58.4217, 15.5888)
    southwest = Coordinate(58.4001, 15.5428)
    center = (northeast + southwest) / 2
    current_round_id = get_round_from_date(datetime.now())
    last_round_id = current_round_id - 1
    print(f"Current round ID: {last_round_id}")

    # Fetch zones in the area
    turf_api = TurfAPI()
    zones = turf_api.fetch_zones_in_area(northeast, southwest)

    # Scrape takeover data for a specific zone
    zone_name = "Resecentrum"
    scraper = ZundinScraper()
    full_takeovers_df = pd.DataFrame()
    for round_id in range(160, 172):
        round_takeovers_df = scraper.get_takeover_data(zone_name, round_id)
        full_takeovers_df = pd.concat([full_takeovers_df, round_takeovers_df], ignore_index=True)

    # Cool statistics B)
    zone_stats = ZoneStats(zone_name, full_takeovers_df)
    estimated_hold_time = zone_stats.estimate_hold_time(datetime.now())
    zone_stats.hourly_histogram()
    zone_stats.daily_histogram()
    zone_stats.show_plots()


    # for zone in zones:
    #     df = scraper.get_takeover_data(zone.name, last_round_id)
    #     estimate_hold_time(df)

    # Draw map
    gui = FoliumGUI(center)
    gui.draw_bbox(northeast, southwest)
    gui.draw_zones(zones)
    gui.save_map("map.html")