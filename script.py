import icalendar
from icalendar import Calendar
import os
from dataclasses import dataclass
from datetime import date
from typing import List, Dict, TypedDict
import json

ICAL_DATA_FOLDER = './data/schulferien'
BUNDESLAENDER = ['BW', 'BY', "BE", "BB", 'HB', 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH']

class Holiday(TypedDict):
    holiday_type: str
    start: date
    end: date

HolidayDict = Dict[str, Dict[str, List[Holiday]]]

def icalendar_event_to_holiday(e: icalendar.Event):
    return {
        'holiday_type': str(e['SUMMARY']),
        'start': e['DTSTART'].dt,
        'end': e['DTEND'].dt}

def get_holidays_from_ics_file(file_path) -> List[Holiday]:
    holidays = []
    with open(file_path) as f:
        ical_data = f.read()
        cal = Calendar.from_ical(ical_data)
        for e in cal.walk('vevent'):
            moped = icalendar_event_to_holiday(e)
            holidays.append(moped)
    return holidays


def duplicate_overflowing_holidays_into_next_year(data: HolidayDict):
    # All Holidays are only listed once in the year in which they start.
    # This function duplicates Holidays which go from december to january of the next year into the next year
    years = list(data.keys())
    for year in reversed(years[:-1]):
        last_date_of_year = date(int(year), 12, 31)
        next_year = str(int(year) + 1)
        for bundesland in BUNDESLAENDER:
            for holiday in data[year][bundesland]:
                if holiday['end'] > last_date_of_year:
                    data[next_year][bundesland].append(holiday)
    return data

def main():
    years = sorted([dir for dir in os.listdir(ICAL_DATA_FOLDER)])
    
    data: HolidayDict = {}
    for year in years:
        data[year] = {}
        for bundesland in BUNDESLAENDER:
            file_path = os.path.join(ICAL_DATA_FOLDER, year, f'{bundesland}.ics')
            data[year][bundesland] = get_holidays_from_ics_file(file_path)

    data = duplicate_overflowing_holidays_into_next_year(data)

    with open('data.json', 'w') as f:
        # Default str necessary for datetime.date
        json.dump(data, f, default=str, indent=4)



if __name__ == "__main__":
    main()