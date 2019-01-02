import datetime
import calendar
import pandas as pd


def is_third_friday(date):
    return date.weekday() == 4 and 15 <= date.day <= 21


def month_fridays(year, month):
    cal = calendar.Calendar(firstweekday=6)
    monthcal = cal.monthdatescalendar(year, month)
    fridays = [day
               for week in monthcal
               for day in week
               if (day.weekday() == calendar.FRIDAY and
                   day.month == month)]
    return fridays


def month_expiry(year, month):
    return month_fridays(year, month)[2]


def this_expiry(date):
    return month_expiry(date.year, date.month)


def next_expiry(date):
    this_month = this_expiry(date)
    if this_month > date:
        return this_month
    else:
        next_month = date + pd.tseries.offsets.BMonthBegin()
        return this_expiry(next_month)


def days_to_expiry(date=datetime.date.today()):
    expiry = next_expiry(date)
    return pd.date_range(date, expiry, freq=pd.tseries.offsets.BDay()).size


def years_to_expiry(date=datetime.date.today()):
    trading_days = 252
    return days_to_expiry(date) / trading_days


if __name__ == '__main__':
    print(next_expiry(datetime.date(2019, 1, 17)))
    print(next_expiry(datetime.date(2019, 1, 18)))
    print(next_expiry(datetime.date(2019, 1, 19)))
    print(days_to_expiry())
    print(years_to_expiry())
