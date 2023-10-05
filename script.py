import icalendar
from icalendar import Calendar
import os
from dataclasses import dataclass
from datetime import date
from typing import List, Dict, TypedDict
import json

BUNDESLAENDER = ['BW', 'BY', "BE", "BB", 'HB', 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH']

class Holiday(TypedDict):
    holiday_type: str
    start: date
    end: date
    id: str

HolidayDict = Dict[str, Dict[str, List[Holiday]]]

def icalendar_event_to_holiday(e: icalendar.Event, id):
    summary = str(e['SUMMARY']).replace(' in Deutschland', '')
    return {
        'holiday_type': summary,
        'start': e['DTSTART'].dt,
        'end': e['DTEND'].dt,
        'id': id}

def get_holidays_from_ics_file(file_path, year, bundesland) -> List[Holiday]:
    holidays = []
    with open(file_path) as f:
        ical_data = f.read()
        cal = Calendar.from_ical(ical_data)
        index = 0
        for e in cal.walk('vevent'):
            id = f'{year}-{bundesland}-{index}'
            moped = icalendar_event_to_holiday(e, id)
            holidays.append(moped)
            index+=1
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

def ics_dir_to_json(in_dir, out_path):
    years = sorted([dir for dir in os.listdir(in_dir)])
    
    data: HolidayDict = {}
    for year in years:
        data[year] = {}
        for bundesland in BUNDESLAENDER:
            filename = f'{bundesland}.ics'
            schulferien_path = os.path.join(in_dir, year, filename)
            schmollidays = get_holidays_from_ics_file(schulferien_path, year, bundesland)
            data[year][bundesland] = schmollidays


    data = duplicate_overflowing_holidays_into_next_year(data)

    with open(out_path, 'w', encoding='utf8') as f:
        # Default str necessary for datetime.date
        json.dump(data, f, default=str, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    ics_dir_to_json('./data/schulferien', 'schulferien.json')
    ics_dir_to_json('./data/gesetzliche_feiertage', 'feiertage.json')