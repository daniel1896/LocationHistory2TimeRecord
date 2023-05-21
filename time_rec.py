"""
Create a time record of a certain location using Google Location History data.
The location history data is downloaded from Google Takeout and is represented as a JSON file.

Created by: Daniel Henning
Date: 2023-05-21
"""

import os
import argparse
import json
from datetime import datetime, timedelta
from pytz import timezone

from utils import create_excel_file, is_within_radius


class TimeRecord:
    def __init__(self, target_latitude, target_longitude, target_radius):
        self.target_lat = target_latitude
        self.target_lon = target_longitude
        self.target_radius = target_radius

        self.start_time = []
        self.end_time = []
        self.duration = []

    def create_time_record(self, location_history_file, print_info=True):
        # Load the JSON data
        with open(location_history_file) as file:
            data = json.load(file)

        # define time zone
        tz = timezone('Europe/Berlin')

        # Extract relevant information
        timeline = data['timelineObjects']
        # timeline is a list of dictionaries containing the following two keys:
        # - 'activitySegment': contains information about the activity (e.g., walking, driving, etc.)
        # - 'placeVisit': contains information about the visited place (e.g., latitude, longitude, etc.)

        # for-loop over all entries in the timeline, if the entry is a 'placeVisit' entry
        for i, entry in enumerate(timeline):
            # Check if the entry is a 'placeVisit' entry
            if 'placeVisit' in entry:
                # check if the location is within the target area
                latitude = entry['placeVisit']['location']['latitudeE7'] * 1e-7
                longitude = entry['placeVisit']['location']['longitudeE7'] * 1e-7
                if is_within_radius(latitude, longitude, self.target_lat, self.target_lon, self.target_radius):
                    # Extract the time information ('2023-05-01T09:37:47.298Z')
                    ts_start = datetime.strptime(entry['placeVisit']['duration']['startTimestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    ts_end = datetime.strptime(entry['placeVisit']['duration']['endTimestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    ts_start = tz.fromutc(ts_start)
                    ts_end = tz.fromutc(ts_end)
                    duration = ts_end - ts_start
                    self.start_time.append(ts_start)
                    self.end_time.append(ts_end)
                    self.duration.append(duration)

                    # print the time records of the target location
                    if print_info:
                        print('----------------------------------------')
                        print('Start: {} {}'.format(ts_start.date(), ts_start.time()))
                        print('End: {} {}'.format(ts_end.date(), ts_end.time()))
                        print('Duration: {}'.format(duration))

    def remove_breaks(self, break_duration=None):
        """
        Remove breaks shorter than break_duration. If break_duration is None, only register single days (remove all
        breaks).
        :param break_duration: in minutes
        """
        # remove breaks shorter than break_duration, if break_duration is None, only register single days (remove all
        # breaks)
        if break_duration is None:
            break_duration = timedelta(days=1)
        if type(break_duration) is not timedelta:
            assert type(break_duration) is int, 'break_duration must be either None, an integer, or a timedelta object.'
            break_duration = timedelta(minutes=break_duration)

        i = 0
        while i < len(self.start_time) - 1:
            # if on the same day and the break is shorter than break_duration
            if self.start_time[i].date() == self.start_time[i+1].date() \
                    and self.start_time[i+1] - self.end_time[i] < break_duration:
                # remove the break
                self.end_time[i] = self.end_time[i+1]
                self.duration[i] = self.end_time[i] - self.start_time[i]
                del self.start_time[i+1]
                del self.end_time[i+1]
                del self.duration[i+1]
            else:
                i += 1

    def save2excel(self, output_file):
        assert len(self.start_time) == len(self.end_time) == len(self.duration),\
                'The length of the time records does not match.'

        # create an Excel workbook/worksheet
        wb, ws = create_excel_file(output_file, 'time_record')

        for i in range(len(self.start_time)):
            # save the time records of the target location in an Excel file
            ws['A{}'.format(i+2)] = self.start_time[i].date()
            ws['B{}'.format(i+2)] = self.start_time[i].time()
            ws['C{}'.format(i+2)] = self.end_time[i].time()
            ws['D{}'.format(i+2)] = self.duration[i]

        wb.save(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default=None, help='Path to the location history file')
    parser.add_argument('-o', '--output', type=str, default=None, help='Path to the output file')
    parser.add_argument('-lat', '--latitude', type=float, default=None, help='Latitude of the target location')
    parser.add_argument('-lon', '--longitude', type=float, default=None, help='Longitude of the target location')
    parser.add_argument('-r', '--radius', type=int, default=200, help='Radius of the target location in meters')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Minimum duration of the visit in minutes')
    args = parser.parse_args()

    # if input file is not specified, open file dialog
    if args.input is None:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        args.input = filedialog.askopenfilename(filetypes=[('JSON files', '*.json')])

    # if output file is not specified, save file in the same directory
    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + '.xlsx'

    # if the latitude and longitude of the target location are not specified
    if args.latitude is None or args.longitude is None:
        args.latitude = float(input('Please specify the latitude of the target location.'))
        args.longitude = float(input('Please specify the longitude of the target location.'))

    # create a time record of the target location
    time_record = TimeRecord(args.latitude, args.longitude, args.radius)
    time_record.create_time_record(args.input)
    time_record.remove_breaks()
    time_record.save2excel(args.output)
