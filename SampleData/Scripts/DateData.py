from datetime import timedelta, date, datetime
from math import ceil
import os
import holidays
import csv

START_DATE = date(2013, 1, 1)
END_DATE   = date(2017, 1, 2)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def fetchColumns(file):
    columns = []
    with open(file) as column_file:
        reader = csv.reader(column_file)
        for line in reader:
            columns.append(line[0])
    return columns



def suffix(d):
    """
    Returns suffix for day number
    """
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def weekday_uk(d):
    d = (d+1) % 7
    return d if d != 0 else 7

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def get_first_day_of_month(d):
    first_day = datetime(
        d.year, # Copy the year
        d.month, # Copy the month
        1 # Set the day to the first
    )
    
    return first_day.date()

def get_first_day_of_year(d):
    first_day = datetime(
        d.year, # Copy the year
        1, # Copy the month
        1 # Set the day to the first
    )
    
    return first_day.date()

def get_last_day_of_month(d):
    next_month = d.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

def main():
    column_names = fetchColumns("DateColumns.csv")
    us_holidays = holidays.UnitedStates()
    uk_holidays = holidays.UnitedKingdom()
    
    with open(os.path.join("..", "DateDimSampleData.csv"), "w") as date_out_file: # write to parent directory
        writer = csv.DictWriter(date_out_file, fieldnames=column_names)
        #writer.writeheader()

        current_year  = START_DATE.year
        current_month = START_DATE.month

        current_month_start_date = date(current_year, current_month, 1)
        current_year_start_date  = date(current_year, 1, 1)

        for single_date in daterange(START_DATE, END_DATE):
            # Case for new year
            if single_date.year != current_year:
                current_year = single_date.year
                current_year_start_date  = date(current_year, 1, 1)
            # Case for new month
            if single_date.month != current_month:
                current_month = single_date.month
                current_month_start_date = date(current_year, current_month, 1)
            
            date_data = dict()

            date_data["DateKey"] = single_date.strftime("%Y%m%d")
            date_data["Date"]    = single_date
            
            date_data["FullDateUK"]  = single_date.strftime("%d-%m-%Y")
            date_data["FullDateUSA"] = single_date.strftime("%m-%d-%Y")
            
            date_data["DayOfMonth"] = single_date.strftime("%m")
            date_data["DaySuffix"]  = suffix(single_date.day)
            date_data["DayName"]    = single_date.strftime("%A")

            date_data["DayOfWeekUK"]  = weekday_uk(single_date.isoweekday())
            date_data["DayOfWeekUSA"] = single_date.isoweekday()

            date_data["DayOfWeekInMonth"] = (current_month_start_date.isoweekday()-1 + single_date.day ) // 7
            date_data["DayOfWeekInYear"]  = (current_year_start_date.isoweekday()-1  + (single_date - current_year_start_date).days ) // 7

            date_data["DayOfYear"]   = (single_date - current_year_start_date).days + 1
            date_data["WeekOfMonth"] = week_of_month(single_date)
            date_data["WeekOfYear"]  = single_date.isocalendar()[1]

            date_data["Month"] = single_date.month
            date_data["MonthName"] = single_date.strftime("%B")

            date_data["Year"] = single_date.strftime("%Y")

            date_data["MonthYear"] = single_date.strftime("%b-%Y")
            date_data["MMYYYY"] = single_date.strftime("%m%Y")

            date_data["FirstDayOfMonth"] = get_first_day_of_month(single_date)
            date_data["LastDayOfMonth"]  = get_last_day_of_month(single_date)

            date_data["FirstDayOfYear"] = get_first_day_of_year(single_date)
            date_data["LastDayOfYear"] = single_date.replace(month=12, day=31)
            
            date_data["IsHolidayUSA"] = 1 if single_date in us_holidays else 0
            date_data["HolidayUSA"] = us_holidays.get(single_date,"") #.replace("'","\\'").replace(",","\\,")
            
            date_data["IsHolidayUK"] = 1 if single_date in uk_holidays else 0
            date_data["HolidayUK"] = uk_holidays.get(single_date,"") #.replace("'","\\'").replace(",","\\,")

            date_data["IsWeekday"] = 1 if 0 <= single_date.weekday() < 5 else 0


            writer.writerow(date_data)

if __name__=="__main__":
    main()