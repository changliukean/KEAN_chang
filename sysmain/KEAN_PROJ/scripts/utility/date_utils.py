import datetime;
from datetime import timedelta;
import calendar;

from dateutil import relativedelta
from dateutil.relativedelta import relativedelta


NERC_HOLYDAYS_LIST = ['2014-01-01','2014-05-26','2014-07-04','2014-09-01','2014-11-27','2014-12-25',
                      '2017-01-02','2017-05-29','2017-07-04','2017-09-04','2017-11-23','2017-12-25',
                      '2018-01-01','2018-05-28','2018-07-04','2018-09-03','2018-11-22','2018-12-25',
                      '2019-01-01','2019-05-27','2019-07-04','2019-09-02','2019-11-28','2019-12-25',
                      '2020-01-01','2020-05-25','2020-07-04','2020-09-07','2020-11-26','2020-12-25',
                      '2021-01-01','2021-05-31','2021-07-05','2021-09-06','2021-11-25','2021-12-25'
                    ];


MONTH_NUMBER_DICT = {'January':1,'Febuary':2,'March':3,'April':4,\
                     'May':5,'June':6,'July':7,'August':8,\
                     'September':9,'October':10,'November':11,'December':12};




def get_dates_list(start_date_str, end_date_str):
    date1 = start_date_str;
    date2 = end_date_str;
    start = datetime.datetime.strptime(date1, '%Y-%m-%d');
    end = datetime.datetime.strptime(date2, '%Y-%m-%d');
    step = datetime.timedelta(days=1);
    dates_list = [];
    while start <= end:
        dates_list.append(start.date());
        start += step;
    return dates_list;



def is_weekend_or_holiday(date_str):
    weekno = date_str.weekday();
    # us_holidays = holidays.UnitedStates();
    global NERC_HOLYDAYS_LIST;
    if weekno >= 5 or str(date_str) in NERC_HOLYDAYS_LIST:
        return True;
    else:
        return False;


def get_sql_where_clause_for_dates(dates_list):
    sql_where_clause = " in (";
    for date_str in dates_list:
        date_str = str(date_str);
        sql_where_clause += "\'" + date_str + "\' , ";
    sql_where_clause = sql_where_clause[:-2] +  " ) ";
    return sql_where_clause;


def get_date_ahead(current_date, days=1):
    date_ahead = current_date - timedelta(days);
    return date_ahead;


def get_date_after(current_date, days=1):
    date_after = current_date + timedelta(days);
    return date_after;


def get_date_from_str(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date();


def calc_forecast_monthly_headers(report_year, report_month):

    column_headers = []
    column_year = str(report_year)[-2:]
    column_headers.append('Jan-'+column_year)
    column_headers.append('Feb-'+column_year)
    column_headers.append('Mar-'+column_year)
    column_headers.append('Apr-'+column_year)
    column_headers.append('May-'+column_year)
    column_headers.append('Jun-'+column_year)
    column_headers.append('Jul-'+column_year)
    column_headers.append('Aug-'+column_year)
    column_headers.append('Sep-'+column_year)
    column_headers.append('Oct-'+column_year)
    column_headers.append('Nov-'+column_year)
    column_headers.append('Dec-'+column_year)
    column_headers.append('FY-'+column_year)

    return column_headers[report_month-1]


def calc_forecast_monthly_headers_month(report_month):

    column_headers = []
    column_headers.append('January')
    column_headers.append('Febuary')
    column_headers.append('March')
    column_headers.append('April')
    column_headers.append('May')
    column_headers.append('June')
    column_headers.append('July')
    column_headers.append('August')
    column_headers.append('September')
    column_headers.append('October')
    column_headers.append('November')
    column_headers.append('December')

    return column_headers[report_month-1];


def get_month_number(month):
    return MONTH_NUMBER_DICT[month];

def get_date_by_scenario(scenario):
    year = scenario.split(" ")[0];
    month = scenario.split(" ")[1];
    month_str = str(MONTH_NUMBER_DICT[month]) if len(str(MONTH_NUMBER_DICT[month])) > 1 else '0' + str(MONTH_NUMBER_DICT[month]);
    return year+"-"+month_str+"-01";

def get_month_dates_list(year, start_month, end_month):
    month_dates_list = [];
    for month in range(start_month, end_month+1):
        month_str = str(month) if len(str(month)) > 1 else "0"+str(month);
        date_str = str(year) + "-" + month_str + "-" + str(calendar.monthrange(year, month)[1]);
        month_dates_list.append(date_str);
    return month_dates_list;


def get_dates_info_from_amr_scenario(amr_scenario):
    year = int(amr_scenario.split(" ")[0]);
    end_month = MONTH_NUMBER_DICT[amr_scenario.split(" ")[1]];

    start_month = 1;
    last_month = 12;

    actuals_month_dates_list = get_month_dates_list(year, start_month, end_month);
    budget_month_dates_list = get_month_dates_list(year, start_month, last_month);
    estimate_month_dates_list = get_month_dates_list(year, end_month+1, last_month);

    return actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list;




def calc_month_end(period, date_type='datetime'):
    #requires period be datatime not a string
    #default behavior returns datetime, option to return date
    period_year = period.year
    period_month = period.month
    month_end_day = calendar.monthrange(period_year, period_month)[1]

    if date_type == 'date':
        return datetime.date(period_year, period_month, month_end_day)
    else:
        return datetime.datetime(period_year, period_month, month_end_day)


def calc_next_month_end(period, date_type='datetime'):
    next_period = period + relativedelta(months=+1)
    period_year = next_period.year
    period_month = next_period.month
    month_end_day = calendar.monthrange(period_year, period_month)[1]

    if date_type == 'date':
        return datetime.date(period_year, period_month, month_end_day)
    else:
        return datetime.datetime(period_year, period_month, month_end_day)


def calc_prior_month_end(period, date_type='datetime'):
    prior_period = period + relativedelta(months=-1)
    period_year = prior_period.year
    period_month = prior_period.month
    month_end_day = calendar.monthrange(period_year, period_month)[1]

    if date_type == 'date':
        return datetime.date(period_year, period_month, month_end_day)
    else:
        return datetime.datetime(period_year, period_month, month_end_day)


def get_last_amr_scenario(current_amr_scenario):
    year = int(current_amr_scenario.split(" ")[0]);
    month = MONTH_NUMBER_DICT[current_amr_scenario.split(" ")[1]];

    last_month = 0;
    last_year = year;
    if month != 1:
        last_month = month - 1;
    else:
        last_month = 12;
        last_year = year - 1;

    last_amr_scenario = str(last_year) + " " + calc_forecast_monthly_headers_month(last_month) + " AMR";

    return last_amr_scenario;
