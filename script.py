import icalendar
from icalendar import Calendar
import os
from dataclasses import dataclass
from datetime import date
from typing import List, Dict, TypedDict
import json

class Holiday(TypedDict):
    holiday_type: str
    start: date
    end: date

def icalendar_event_to_holiday(e: icalendar.Event):
    return {
        'holiday_type': str(e['SUMMARY']),
        'start': e['DTSTART'].dt,
        'end': e['DTEND'].dt}

def getmopedsschmopeds(file_path) -> List[Holiday]:
    holidays = []
    with open(file_path) as f:
        ical_data = f.read()
        cal = Calendar.from_ical(ical_data)
        for e in cal.walk('vevent'):
            moped = icalendar_event_to_holiday(e)
            holidays.append(moped)
    return holidays


ical_data_folder = './ics'
# years = [dir for dir in os.listdir(ical_data_folder)]
years = sorted(['2023', '2024'])
data: Dict[str, Dict[str, List[Holiday]]] = {}

bundeslaender = ['BW', 'BY', "BE", "BB", 'HB', 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH']

print(years)
for year in years:
    data[year] = {}
    for bundesland in bundeslaender:
        file_path = os.path.join(ical_data_folder, year, f'{bundesland}.ics')
        data[year][bundesland] = getmopedsschmopeds(file_path)



for year in reversed(years[:-1]):
    last_date_of_year = date(int(year), 12, 31)
    next_year = str(int(year) + 1)
    for bundesland in bundeslaender:
        for holiday in data[year][bundesland]:
            if holiday['end'] > last_date_of_year:
                data[next_year][bundesland].append(holiday)


with open('data.json', 'w') as f:
    # Default str necessary for datetime.date
    json.dump(data, f, default=str, indent=4)