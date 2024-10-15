from matplotlib import pyplot as plt
from datetime import datetime
import pandas as pd

class ZoneStats:
    def __init__(self, zone_name, takeovers_df):
        self.zone_name = zone_name
        self.takeovers_df = takeovers_df    # Takeovers + Assists


    def hourly_histogram(self):
        """Plot the number of takeovers per hour of the day"""
        df = self.takeovers_df.copy()

        df['date'] = pd.to_datetime(df['date'])
        df['hour_of_day'] = df['date'].dt.hour
        df['weekday'] = df['date'].dt.weekday
        df['hour_of_week'] = df['weekday'] * 24 + df['hour_of_day']

        plt.figure(figsize=(10, 6))
        plt.hist(df['hour_of_week'], bins=range(0, 24*7 + 1), edgecolor='black')
        plt.title('Number of Takeovers by Hour of the Week')
        plt.xlabel('Hour of the Week')
        plt.ylabel('Number of Takeovers')
        plt.grid(True)


    def daily_histogram(self):
        """Plot the number of takeovers per day of the week"""
        df = self.takeovers_df.copy()

        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.weekday

        plt.figure(figsize=(10, 6))
        plt.hist(df['weekday'], bins=range(0, 8), edgecolor='black')
        plt.title('Number of Takeovers by Day of the Week')
        plt.xlabel('Day of the Week')
        plt.ylabel('Number of Takeovers')
        plt.grid(True)


    def show_plots(self):
        plt.show()


    def estimate_hold_time(self, date: datetime):
        estimated_hold_time = 0

        print("Estimating hold time...")

        # TODO: Implement hold time estimation

        print(f"Estimated hold time at {date} is: {estimated_hold_time} hours")