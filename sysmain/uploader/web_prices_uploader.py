import pandas as pd;
import sys;
from pathlib import Path;
import datetime;
sys.path.insert(0, str(Path(__file__).parents[2])+r'/sysmain/KEAN_PROJ/scripts/utility');
import date_utils;

from datetime import date;
from datetime import *;
from calendar import *;

PRICES_TAB_NAME_DICT = {'Lightstone':['commodity_curves','libor_curves']}

def upload_prices(submit_file, company, scenario):
    prices_upload_list = read_prices_input(submit_file, company, scenario);
    return prices_upload_list;



def read_prices_input(full_file_path, company, scenario):
    tab_name_list = PRICES_TAB_NAME_DICT[company];

    prices_upload_list = [];

    for tab_name in tab_name_list:
        if tab_name == 'commodity_curves':
            com_curve_df = pd.read_excel(full_file_path, tab_name, header=0);
            com_curve_list = read_commodity(com_curve_df, scenario);
            print (len(com_curve_list));
            prices_upload_list += com_curve_list;

        if tab_name == 'libor_curves':
            libor_curve_df = pd.read_excel(full_file_path, tab_name, header=0);
            libor_curve_list = read_libor(libor_curve_df, scenario);
            print (len(libor_curve_list));
            prices_upload_list += libor_curve_list;




    return prices_upload_list;


def get_hours(period):
    ''' given a date returns a tuple of On/Off Peak hours for month'''

    dst_spring = [date(2008, 3, 9), date(2009, 3, 8), date(2010, 3, 14),
        date(2011, 3, 13), date(2012, 3, 11), date(2012, 3, 10), date(2014, 3, 9),
        date(2015, 3, 8), date(2016, 3, 13), date(2017, 3,12)]

    dst_fall = [date(2015, 11, 1), date(2016, 11, 6), date(2017, 11, 5),
        date(2018, 11, 4)]
    nerc_holidays = [date(2017, 1, 2), date(2017, 5, 29) , date(2017, 7, 4), date(2017, 9, 4), date(2017, 11, 23), date(2017, 12, 25)]

    ''' loop through days in month '''
    month_end_day = monthrange(period.year, period.month)[1]
    hours_on = 0
    hours_off = 0
    for i in range(1, month_end_day+1):
        current_day = date(period.year, period.month, i)
        if current_day in dst_spring:
            hours_off += 23
        elif current_day in dst_fall:
            hours_off += 25
        elif current_day in nerc_holidays:
            hours_off += 24
        elif current_day.weekday() in [5,6]:
            hours_off += 24
        else:
            hours_on += 16
            hours_off += 8

    return (hours_on, hours_off)

def read_commodity(com_curve_df, scenario):
    com_curve_list = [];
    print ("com_curve_df:", len(com_curve_df));
    """
        As Of	Contract	AEP-Dayton M2M Pk	AEP-Dayton M2M OPk	Texas Gas Zn1 M2M Fwd	Lebanon Hub-Ohio M2M Fwd	Tx Eastern E LA M2M Fwd	Henry Hub M2M Fwd
    """

    valuation_date_list = list(com_curve_df['As Of']);
    period_list = list(com_curve_df['Contract']);
    prices_column_list = [item for item in com_curve_df.columns if item not in ['As Of','Contract']];
    # print (prices_column_list);

    prices_list = [];


    atc_price_list = [];
    onpeak_price_list = [];
    offpeak_price_list = [];


    for column in prices_column_list:
        instrument_id_list = [column for i in range(0, len(valuation_date_list))];
        prices_list.append([list(com_curve_df[column]), instrument_id_list]);

        if column == 'AEP-Dayton M2M Pk':
            onpeak_price_list = [list(com_curve_df[column]), instrument_id_list];
        if column == 'AEP-Dayton M2M OPk':
            offpeak_price_list = [list(com_curve_df[column]), instrument_id_list];

    for i in range(0, len(period_list)):
        temp_period = period_list[i];
        hours = get_hours(temp_period);
        # print (hours);
        # print (onpeak_price_list[0][i], offpeak_price_list[0][i]);
        atc_price_list.append((onpeak_price_list[0][i] * hours[0] + offpeak_price_list[0][i] * hours[1]) / (hours[0] + hours[1]))


    prices_list.append([atc_price_list, ['AD Hub ATC - Monthly Strip' for i in range(0, len(valuation_date_list))]]);


    valuation_period_prices_list = [];
    for temp_price_list in prices_list:
        scenario_list = [scenario for i in range(0, len(valuation_date_list))];
        temp_combo_list = [scenario_list,valuation_date_list, period_list, temp_price_list[0],temp_price_list[1]];
        valuation_period_prices_list += list(zip(*temp_combo_list));



    print ("com upload list: ",len(valuation_period_prices_list));

    return valuation_period_prices_list;


def read_libor(libor_curve_df, scenario):
    scenario_list = [scenario for i in range(0, len(libor_curve_df))];
    libor_curve_upload_list = [scenario_list];
    print ("libor_curve_df:", len(libor_curve_df));

    for item in libor_curve_df.columns:
        libor_curve_upload_list.append(list(libor_curve_df[item]));

    libor_curve_upload_list = list(zip(*libor_curve_upload_list));

    return libor_curve_upload_list;
