from matplotlib import pyplot as plt
from datetime import datetime
import pandas as pd

class ZoneStats:
    def __init__(self, zone_name, visits_df):
        self.zone_name = zone_name
        self.visits_df = visits_df    # Takeovers + Assists

        # takeovers are where the hold_time > 0
        self.takeovers_df = self.visits_df[self.visits_df['hold_time'] > 0]
        self.assists_df = self.visits_df[self.visits_df['hold_time'] == 0]

    def hourly_histogram(self):
        """Plot the number of takeovers per hour of the day"""
        df = self.takeovers_df.copy()

        df['visit_date'] = pd.to_datetime(df['visit_date'])
        df['hour_of_day'] = df['visit_date'].dt.hour
        df['weekday'] = df['visit_date'].dt.weekday
        df['hour_of_week'] = df['weekday'] * 24 + df['hour_of_day']

        plt.figure(figsize=(10, 6))
        plt.hist(df['hour_of_week'], bins=range(0, 24*7 + 1), edgecolor='black')
        plt.title('Number of Takeovers by Hour of the Week')
        plt.xlabel('Hour of the Week')
        plt.ylabel('Number of Visits')
        plt.grid(True)


    def daily_histogram(self):
        """Plot the number of takeovers per day of the week"""
        df = self.takeovers_df.copy()

        df['visit_date'] = pd.to_datetime(df['visit_date'])
        df['weekday'] = df['visit_date'].dt.weekday

        plt.figure(figsize=(10, 6))
        plt.hist(df['weekday'], bins=range(0, 8), edgecolor='black')
        plt.title('Number of Takeovers by Day of the Week')
        plt.xlabel('Day of the Week')
        plt.ylabel('Number of Takeovers')
        plt.grid(True)


    def show_plots(self):
        plt.show()


    def estimate_hold_time(self, date: datetime, method='mean'):
        if method == 'mean':
            return self._mean_hold_time()
        elif method == 'fourier':
            return self._fourier_hold_time(date)
        else:
            raise ValueError("Invalid method for estimating hold time.")


    def _mean_hold_time(self):
        return self.takeovers_df['hold_time'].mean()


    def _fourier_hold_time(self, date: datetime):
        raise NotImplementedError("Fourier method not implemented yet.")