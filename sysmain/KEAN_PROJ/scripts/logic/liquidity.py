from pathlib import Path;
import os
import sys

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_liquidity;
import db_controller;


import datetime
from datetime import date
from calendar import monthrange;

import math
from math import pow
from datetime import timedelta;


# from sympy.solvers import solve;
# from sympy import Symbol;




import pandas as pd

"""
    Here we define all the hardcoded values as global constants
    in the future, we will use separate logic to replace part of them
"""
MIN_CASH = 50000000;
YEAR_DAYS = 360;

OID = 410714.29 * 12;
DFC = 605031.96 * 12;
ETR = 0.472684;
TAX_SPLIT = {3:0.2623, 6:0.2459, 9:0.2459, 12:0.2459}; #use later




TAX_DEPRECIATION_RESULT = [];




def process_liquidity(conn_ins, scenario, company, version, valuation_date):
    # instrument_id = 'LIBOR-1MO';
    # # valuation_date = datetime.date(2017,6,28);
    # valuation_date = '2017-06-28';
    # libor_df = db_controller_liquidity.get_all_libor(conn_ins, valuation_date, instrument_id);
    # print (len(libor_df));

    scenario_year = int(scenario.split(" ")[0]);

    month_number = date_utils.get_month_number(scenario.split(" ")[1]);

    forecast_start = date(scenario_year, month_number+1, 1);
    # forecast_start = date(2017,8,1)

    forecast_end = date(scenario_year+4,12,31)
    scenario_start = date(scenario_year,1,30)
    scenario_debt_inception = 'Actuals'
    # scenario = '2017 July AMR'
    # company = 'Lightstone'
    # version = 'v5';
    entity = 'Holdco'
    instrument_id = 'Lightstone TLB'

    maintenance_capex_dict = {};
    ltsa_capex_dict = {};

    maintenance_capex_df = db_controller_liquidity.get_maintenance_capex(conn_ins, company, scenario, version);
    ltsa_capex_df = db_controller_liquidity.get_ltsa_capex(conn_ins, company, scenario, version);


    print (len(maintenance_capex_df));

    # for item in maintenance_capex_df:
    #     print (item);

    maintenance_capex_df.sort_values('period');

    print (len(ltsa_capex_df));

    ltsa_capex_df.sort_values('period');

    year_list = list(range(int(scenario.split(" ")[0]), int(scenario.split(" ")[0])+5));

    print (year_list);

    for year in year_list:
        print (year);
        begin_date = datetime.date(year = year, month = 1, day = 1);
        end_date = datetime.date(year = year, month = 12, day = 31);
        maintenance_capex_list = list(maintenance_capex_df.loc[(maintenance_capex_df['period'] >= begin_date) & (maintenance_capex_df['period'] <= end_date)]['sum(value)']);
        ltsa_capex_list = list(ltsa_capex_df.loc[(ltsa_capex_df['period'] >= begin_date) & (ltsa_capex_df['period'] <= end_date)]['sum(value)']);
        maintenance_capex_dict[year] = maintenance_capex_list;
        ltsa_capex_dict[year] = ltsa_capex_list;

    # for item in maintenance_capex_dict:
    #     print (maintenance_capex_dict[item]);
    #
    # for item in ltsa_capex_dict:
    #     print (ltsa_capex_dict[item]);


    periods = pd.date_range(scenario_start, forecast_end, freq='M')

    # periods_date = [item.date() for item in periods]

    df_liquidity = pd.DataFrame(periods, columns = ['period'])
    df_liquidity.set_index(['period'], inplace=True)
    df_liquidity['TLB BOP'] = 0
    df_liquidity['TLB Addl Borrow'] = 0
    df_liquidity['TLB Amort'] = 0
    df_liquidity['TLB Prepay'] = 0
    df_liquidity['TLB EOP'] = 0
    df_liquidity['TLB Change'] = 0
    df_liquidity['TLC BOP'] = 0
    df_liquidity['TLC Addl Borrow'] = 0
    df_liquidity['TLC Amort'] = 0
    df_liquidity['TLC Prepay'] = 0
    df_liquidity['TLC EOP'] = 0
    df_liquidity['Revolver Change'] = 0
    df_liquidity['LIBOR'] = 0
    df_liquidity['TLB Float Rate'] = 0
    df_liquidity['Swap Fix Rate'] = 0
    df_liquidity['Swap Avg Daily Balance'] = 0
    df_liquidity['TLB Int Exp'] = 0
    df_liquidity['TLC Float Rate'] = 0
    df_liquidity['TLC Int Exp'] = 0
    df_liquidity['Int Exp'] = 0
    df_liquidity['EBITDA'] = 0
    df_liquidity['Tax Depreciation'] = 0
    df_liquidity['Taxable Interest'] = 0
    df_liquidity['Eff Tax Rate'] = 0
    df_liquidity['Est Tax Dist'] = 0
    df_liquidity['Cash BOP'] = 0
    df_liquidity['Capex'] = 0
    df_liquidity['Change Work Cap'] = 0
    df_liquidity['Other Cash Use'] = 0
    df_liquidity['Distributions'] = 0
    df_liquidity['Cash EOP'] = 0
    df_liquidity['DSRA BOP'] = 0
    df_liquidity['DSRA EOP'] = 0
    df_liquidity['DSRA Change'] = 0
    df_liquidity['Excess Cash'] = 0

    # sys.exit();
    df_liquidity = build_debt(conn_ins, df_liquidity, forecast_start, forecast_end)
    df_liquidity['TLB Change'] = df_liquidity['TLB EOP'].diff()
    df_liquidity.set_value(date(2017, 1,31), 'TLB Change', 0)   #no diff for first entry
    df_libor_all = db_controller_liquidity.get_all_libor(conn_ins,valuation_date, 'LIBOR-1MO')

    df_liquidity = build_libor(df_liquidity, df_libor_all, forecast_start, valuation_date)
    # sys.exit();
    df_liquidity['TLB Float Rate'] = df_liquidity['LIBOR'] + 0.045
    df_swap = build_daily_swap(conn_ins,valuation_date, forecast_start, forecast_end)
    df_liquidity = build_swap_rate(df_liquidity, df_swap, forecast_start)
    df_liquidity = build_tlb_int_exp(df_liquidity, forecast_start)
    df_liquidity = build_int_exp_actual(df_liquidity)
    df_liquidity.loc[forecast_start:,['TLC Float Rate']] = df_liquidity['LIBOR'] + 0.045
    df_liquidity.loc[forecast_start:,['TLC Int Exp']] = df_liquidity['TLC Float Rate'] * df_liquidity['TLC BOP'] * df_liquidity.index.day / YEAR_DAYS
    df_liquidity['Int Exp'] = df_liquidity['TLB Int Exp'] + df_liquidity['TLC Int Exp']
    df_liquidity = db_controller_liquidity.build_ebitda(conn_ins, df_liquidity, scenario, company, version)
    df_liquidity = db_controller_liquidity.build_capex(conn_ins, df_liquidity, scenario, company, version)
    df_cash = db_controller_liquidity.get_cash(conn_ins, scenario)
    df_liquidity = build_cash_actuals(df_liquidity, df_cash)
    df_liquidity = build_dsra(conn_ins, df_liquidity, scenario)
    df_liquidity['DSRA Change'] = -df_liquidity['DSRA EOP'].diff()
    df_liquidity.set_value(date(2017, 1,31), 'DSRA Change', 0)   #no diff for first entry
    df_liquidity = build_distributions(conn_ins, df_liquidity, scenario)
    df_liquidity = build_other_cash_use(df_liquidity)
    df_liquidity = build_change_work_cap(df_liquidity, forecast_start)

    df_liquidity = build_est_tax_dist(conn_ins, df_liquidity, forecast_start, forecast_end, scenario,version)



    '''iterative search '''
    # for i in range(1):
    #     df_liquidity = build_tlb_bop_eop(df_liquidity)
    #     df_liquidity = search_for_prepay(df_liquidity, forecast_start, MIN_CASH)
    #     df_liquidity = recalc_tlb_amort(df_liquidity, forecast_start)
    #     df_liquidity = recalc_tlb(df_liquidity, forecast_start)
    #     df_liquidity = recalc_tlb_int_exp(df_liquidity, forecast_start)
    #     df_liquidity['Int Exp'] = df_liquidity['TLB Int Exp'] + df_liquidity['TLC Int Exp']
    #     df_liquidity = build_est_tax_dist(conn_ins, df_liquidity, forecast_start, forecast_end, scenario, version)


    #df_cash.to_csv('df_cash.csv')
    #df_swap.to_csv('df_swap.csv')
    df_liquidity.to_csv('df_liquidity.csv')

    # df_tax = build_est_tax_dist_display(conn_ins, df_liquidity, forecast_start, forecast_end, scenario);



    return df_liquidity, TAX_DEPRECIATION_RESULT, maintenance_capex_dict, ltsa_capex_dict;




"""
    cubic spline method

    the input for July/June AMR is already linear interpolated
    which made the cubic spline function here still choppy
    in Augest, we should have original Libor rates and we do cubic spline interpolation by ourselves
"""
def get_smoothed_libor_spot_curve(libor_df, period, valuation_date):
    from scipy.interpolate import interp1d;

    x_axis_term = [(libor_period - valuation_date).days for libor_period in list(libor_df['period'])];

    # print (x_axis_term);
    y_axis_spot_rate = list(libor_df['rate']);
    # y_axis_spot_rate = [item*100000 for item in list(libor_df['rate'])];
    # print (y_axis_spot_rate);
    # print (len(x_axis_term), len(y_axis_spot_rate));

    linear_spline_function = interp1d(x_axis_term, y_axis_spot_rate);
    cubic_spline_function = interp1d(x_axis_term, y_axis_spot_rate, kind='cubic');
    new_y_axis_spot_rate = [cubic_spline_function(item) for item in range(30,2000)];
    # new_y_axis_spot_rate_linear = [linear_spline_function(item) for item in x_axis_term];
    # x_axis_term_sparse = [x_axis_term[i] for i in range(0, len(x_axis_term),10)];
    # y_axis_spot_rate_sparse = [y_axis_spot_rate[i] for i in range(0, len(y_axis_spot_rate), 10)];
    # cubic_spline_function_sparse = interp1d(x_axis_term_sparse, y_axis_spot_rate_sparse, kind='cubic');
    # new_y_axis_spot_rate_sparse = [cubic_spline_function_sparse(item) for item in x_axis_term[:-10]];
    #

    # print (len(y_axis_spot_rate), len(new_y_axis_spot_rate));
    #
    # for item in [y_axis_spot_rate[i]-new_y_axis_spot_rate[i] for i in range(0,len(y_axis_spot_rate))]:
    #     print (item);

    # import matplotlib.pyplot as plt;
    # plt.plot(x_axis_term, new_y_axis_spot_rate);
    # plt.plot(x_axis_term[:5], y_axis_spot_rate[:5],'-', range(30,201), new_y_axis_spot_rate[:171], '-', x_axis_term[:5], new_y_axis_spot_rate_sparse[:5],'--');
    # plt.plot(x_axis_term, new_y_axis_spot_rate, '-', x_axis_term[:-10], new_y_axis_spot_rate_sparse,'--');
    # plt.show();
    # sys.exit();
    new_term_spot = (period - valuation_date).days;
    return cubic_spline_function(new_term_spot);


""" old_method """
# def get_libor(libor_df, period):
#     ''' assumes df is order by period '''
#
#     # if libor_df.iloc[0]['period'] > period:
#     #     print('Error - requested date precedes curve', period)
#     #     return None
#     # elif libor_df.iloc[-1]['period'] < period:
#     #     print('Error - requested date exceeds curve')
#     #     return None
#     # period = period.date();
#     if period > libor_df['period'].max() or period < libor_df['period'].min():
#         print('Error - requested date exceeds curve')
#         return None
#
#     index = 0;
#     while libor_df.iloc[index]['period'] < period:
#         lower_date = libor_df.iloc[index]['period'];
#         lower_value = libor_df.iloc[index]['rate'];
#         index += 1;
#     upper_date = libor_df.iloc[index]['period'];
#     upper_value = libor_df.iloc[index]['rate'];
#     return ((period-lower_date)/(upper_date-lower_date))*(upper_value-lower_value)+lower_value;



# def calc_libor_forward(df_libor_all, valuation_date, period):
#     prior_period = date_utils.calc_prior_month_end(period, 'date')
#     lower_value = get_smoothed_libor_spot_curve(df_libor_all, prior_period, valuation_date)
#     upper_value = get_smoothed_libor_spot_curve(df_libor_all, period, valuation_date);
#     total_days = (period - valuation_date).days
#     forward_days = monthrange(period.year, period.month)[1]
#     # print (forward_days);
#     prior_days = total_days - forward_days
#     """ ALG calculation logic """
#     # forward_rate = pow(1+upper_value/YEAR_DAYS, total_days) / pow(1+lower_value/YEAR_DAYS, prior_days)
#     # print (forward_rate);
#     # forward_rate = (pow(forward_rate, 1/forward_days)-1)*YEAR_DAYS
#     # print ("--------------------");
#     # print (total_days, prior_days, forward_days);
#     # print (upper_value, lower_value, forward_rate);
#     # print (pow((1+upper_value/360),total_days) - pow((1+lower_value/360), prior_days)*pow((1+forward_rate/360),forward_days));
#     """ CL calculation logic """
#     # x = Symbol('x');
#     a =  pow((1+lower_value/YEAR_DAYS),prior_days);
#     b =  pow((1+upper_value/YEAR_DAYS),total_days);
#     # result = solve(((1+x/YEAR_DAYS)**forward_days) * a - b, x);
#     # result = solve(x**2-1,x);
#     forward_rate = (pow(b/a, 1/forward_days) - 1) * YEAR_DAYS;
#     # print (forward_rate);
#     return forward_rate;
#

def get_swap(df, period):
    # print (type(period));
    # print (type(df.iloc[0]['date_start']));
    if period.date() < df.iloc[0]['date_start']:
        return None
    if period.date() > df.iloc[-1]['date_end']:
        return None

    mask = (df['date_start'] <= period.date()) & (df['date_end']>=period.date())
    notional = df[mask]['notional'].values[0]
    rate = df[mask]['fixed_rate'].values[0]

    return (notional, rate)


def build_daily_swap(conn_ins, valuation_date, forecast_start, forecast_end):
    swap_curve = db_controller_liquidity.get_all_swap(conn_ins, 'IR_Swap_1')

    df = pd.DataFrame(pd.date_range(forecast_start, forecast_end, freq='D', name='period'))



    df.set_index(['period'], inplace=True)
    df['swap_rate'] = None
    df['swap_balance'] = None
    df['calc_swap_rate'] = None
    for index, day in df.iterrows():
        #swap = get_swap(swap_curve, day[0])
        swap = get_swap(swap_curve, index)
        #swap_balance = 0 if swap is None else swap[0]
        swap_balance = 0 if swap is None else swap[0]
        swap_rate = 0 if swap is None else swap[1]
        df.set_value(index, ['swap_balance'], swap_balance)
        df.set_value(index, ['swap_rate'], swap_rate)
        df.set_value(index, ['calc_swap_rate'], swap_balance * swap_rate)

    return df


def get_debt_activity(df, activity, period):
    month_start = date(period.year, period.month, 1)
    month_end = date_utils.calc_month_end(period, 'date')
    mask = (df['payment_date'] >= month_start) & (df['payment_date'] <= month_end) & (df['payment_type'] == activity)
    return df[mask]['amount'].sum()


def calc_required_amort(df, instrument_id, as_of_date):
    df_required = df.loc[:as_of_date]
    amort = 0
    for index, row in df_required.iterrows():
        if index.month % 3 == 0:
            amort += 1625000000 * 0.0025
    return amort


def calc_tax_depreciation(entity, new):
    ''' hard code rules for now - move to scenario assumptions '''
    ''' HoldCo reflects goodwill '''
    ''' new is True/False '''
    entities = {'Gavin':28, 'Waterford': 28, 'Lawrenceburg': 28, 'Darby': 20, 'HoldCo': 20}
    depreciation_rate = 1 / entities[entity]
    if new:
        return depreciation_rate / 2
    else:
        return depreciation_rate



def build_debt(conn_ins, df, forecast_start, forecast_end):
    ''' set initial debt balances '''
    tlb_bop = db_controller_liquidity.get_inception_debt_balance(conn_ins, 'Lightstone TLB')
    tlc_bop = db_controller_liquidity.get_inception_debt_balance(conn_ins, 'Lightstone TLC')

    df_debt_activity_tlb = db_controller_liquidity.get_debt_activity_all(conn_ins,'Lightstone TLB')
    df_debt_activity_tlb['payment_date_date'] = pd.to_datetime(df_debt_activity_tlb['payment_date'])
    df_debt_activity_tlc = db_controller_liquidity.get_debt_activity_all(conn_ins,'Lightstone TLC')
    df_debt_activity_tlc['payment_date_date'] = pd.to_datetime(df_debt_activity_tlc['payment_date'])
    last_activity_date_tlb = date_utils.calc_month_end(df_debt_activity_tlb['payment_date_date'].max(), 'date')
    last_activity_date_tlc = date_utils.calc_month_end(df_debt_activity_tlc['payment_date_date'].max(), 'date')

    for index, row in df.iterrows():
        ''' tlb first '''
        tlb_addl_borrow = 0
        tlb_prepay = 0
        tlb_amort = 0
        if date(index.year, index.month, index.day) <= max(last_activity_date_tlb, forecast_start):
            df.set_value(index, 'TLB BOP', tlb_bop)
            tlb_addl_borrow = get_debt_activity(df_debt_activity_tlb, 'additional borrowing', index)
            df.set_value(index, 'TLB Addl Borrow', tlb_addl_borrow)
            tlb_amort = get_debt_activity( df_debt_activity_tlb, 'amortization', index)
            df.set_value(index, 'TLB Amort', tlb_amort)
            tlb_prepay = get_debt_activity(df_debt_activity_tlb, 'prepayment', index)
            df.set_value(index, 'TLB Prepay', tlb_prepay)
            tlb_eop = tlb_bop + tlb_addl_borrow - tlb_amort - tlb_prepay
            df.set_value(index, 'TLB EOP', tlb_eop)
            tlb_bop = tlb_eop

        ''' tlc second '''
        if date(index.year, index.month, index.day) < max(last_activity_date_tlc, forecast_start):
            df.set_value(index, 'TLC BOP', tlc_bop)
            tlc_addl_borrow = get_debt_activity(df_debt_activity_tlc, 'additional borrowing', index)
            df.set_value(index, 'TLC Addl Borrow', tlc_addl_borrow)
            tlc_amort = get_debt_activity(df_debt_activity_tlc, 'amortization', index)
            df.set_value(index, 'TLC Amort',tlc_amort)
            tlc_prepay = get_debt_activity(df_debt_activity_tlc, 'prepayment', index)
            df.set_value(index, 'TLC Prepay',tlc_prepay)
            tlc_eop = tlc_bop + tlc_addl_borrow - tlc_amort - tlc_prepay
            df.set_value(index, 'TLC EOP', tlc_eop)
            tlc_bop = tlc_eop

        ''' forecast period '''
        if date(index.year, index.month, index.day) >= forecast_start:
            # print (index, row['TLB BOP']);
            if row['TLB BOP'] <= 0:
                ''' calc amortization '''
                if index.month % 3 == 0:
                    required_amort = calc_required_amort(df, 'Lightstone TLB', index)
                    cum_prepay = df.loc[:index]['TLB Prepay'].sum()
                    cum_amort = df.loc[:index]['TLB Amort'].sum()
                    tlb_amort = max(min(1625000000*0.0025,required_amort-cum_prepay-cum_amort),0)
                    df.set_value(index, ['TLB Amort'], tlb_amort)

                df.set_value(index, 'TLB BOP', tlb_bop)
                tlb_eop = tlb_bop + tlb_addl_borrow - tlb_amort - tlb_prepay
                df.set_value(index, 'TLB EOP', tlb_bop - tlb_amort)
                tlb_bop = tlb_eop
            if row['TLC BOP'] <= 0:
                df.set_value(index, 'TLC BOP', tlc_bop)
                tlc_eop =  tlc_bop + tlc_addl_borrow - tlc_amort - tlc_prepay
                df.set_value(index, 'TLC EOP', tlc_bop)
                tlc_bop = tlc_eop
    return df






# def build_debt(conn_ins, df_liquidity, forecast_start, forecast_end):
#     ''' set initial debt balances '''
#     tlb_bop = db_controller_liquidity.get_inception_debt_balance(conn_ins,'Lightstone TLB')
#     tlc_bop = db_controller_liquidity.get_inception_debt_balance(conn_ins,'Lightstone TLC')
#
#     df_debt_activity_tlb = db_controller_liquidity.get_debt_activity_all(conn_ins,'Lightstone TLB')
#     # df_debt_activity_tlb['payment_date_date'] = pd.to_datetime(df_debt_activity_tlb['payment_date'])
#     df_debt_activity_tlc = db_controller_liquidity.get_debt_activity_all(conn_ins,'Lightstone TLC')
#     # df_debt_activity_tlc['payment_date_date'] = pd.to_datetime(df_debt_activity_tlc['payment_date'])
#     # print (df_debt_activity_tlb['payment_date'].max());
#     # print (date_utils.calc_month_end(df_debt_activity_tlb['payment_date'].max(), 'date'));
#     # last_activity_date_tlb = date_utils.calc_month_end(df_debt_activity_tlb['payment_date'].max(), 'date')
#     # last_activity_date_tlc = date_utils.calc_month_end(df_debt_activity_tlc['payment_date'].max(), 'date')
#
#     """
#         in case to make the logic consistent in the long run, we change the logic here for the dates
#         we want to include that unnormal prepayment for Lightstone TLB which happens in the forecast period
#         but is an ACTUAL
#         the old logic is "date(index.year, index.month, index.day) <= max(last_activity_date_tlb,forecast_start)"
#         the following is the new logic
#
#         company = 'Lightstone', instrument_id = 'Lightstone TLB', payment_type = 'prepayment', payment_date = '2017-07-03'
#     """
#     special_prepayment_lightstonetlb_df = df_debt_activity_tlb.loc[(df_debt_activity_tlb['company'] == 'Lightstone') &
#                                             (df_debt_activity_tlb['instrument_id'] == 'Lightstone TLB') &
#                                             (df_debt_activity_tlb['payment_type'] == 'prepayment') &
#                                             (df_debt_activity_tlb['payment_date'] == date(2017,7,3))];
#
#     if len(special_prepayment_lightstonetlb_df) > 0:
#         df_liquidity.set_value(date_utils.calc_month_end(special_prepayment_lightstonetlb_df.iloc[0]['payment_date'],'date'), 'TLB Prepay', special_prepayment_lightstonetlb_df.iloc[0]['amount']);
#
#
#
#
#     for index, row in df_liquidity.iterrows():
#         ''' tlb first '''
#         tlb_addl_borrow = 0
#         tlb_prepay = 0
#         tlb_amort = 0
#         if date(index.year, index.month, index.day) <= forecast_start:
#             df_liquidity.set_value(index, 'TLB BOP', tlb_bop)
#             tlb_addl_borrow = get_debt_activity(df_debt_activity_tlb, 'additional borrowing', index)
#             df_liquidity.set_value(index, 'TLB Addl Borrow', tlb_addl_borrow)
#             tlb_amort = get_debt_activity(df_debt_activity_tlb, 'amortization', index)
#             df_liquidity.set_value(index, 'TLB Amort', tlb_amort)
#             tlb_prepay = get_debt_activity(df_debt_activity_tlb, 'prepayment', index)
#             df_liquidity.set_value(index, 'TLB Prepay', tlb_prepay)
#             tlb_eop = tlb_bop + tlb_addl_borrow - tlb_amort - tlb_prepay
#             df_liquidity.set_value(index, 'TLB EOP', tlb_eop)
#             tlb_bop = tlb_eop
#
#         ''' tlc second '''
#         if date(index.year, index.month, index.day) < forecast_start:
#             df_liquidity.set_value(index, 'TLC BOP', tlc_bop)
#             tlc_addl_borrow = get_debt_activity(df_debt_activity_tlc, 'additional borrowing', index)
#             df_liquidity.set_value(index, 'TLC Addl Borrow', tlc_addl_borrow)
#             tlc_amort = get_debt_activity(df_debt_activity_tlc, 'amortization', index)
#             df_liquidity.set_value(index, 'TLC Amort',tlc_amort)
#             tlc_prepay = get_debt_activity(df_debt_activity_tlc, 'prepayment', index)
#             df_liquidity.set_value(index, 'TLC Prepay',tlc_prepay)
#             tlc_eop = tlc_bop + tlc_addl_borrow - tlc_amort - tlc_prepay
#             df_liquidity.set_value(index, 'TLC EOP', tlc_eop)
#             tlc_bop = tlc_eop
#
#         ''' forecast period '''
#         if date(index.year, index.month, index.day) >= forecast_start:
#             if row['TLB BOP'] <= 0:
#                 ''' calc amortization '''
#                 if index.month % 3 == 0:
#                     required_amort = calc_required_amort(df_liquidity, 'Lightstone TLB', index)
#                     cum_prepay = df_liquidity.loc[:index]['TLB Prepay'].sum()
#                     cum_amort = df_liquidity.loc[:index]['TLB Amort'].sum()
#                     tlb_amort = max(min(1625000000*0.0025,required_amort-cum_prepay-cum_amort),0)
#                     df_liquidity.set_value(index, ['TLB Amort'], tlb_amort)
#                 df_liquidity.set_value(index, 'TLB BOP', tlb_bop)
#                 tlb_eop = tlb_bop + tlb_addl_borrow - tlb_amort - tlb_prepay
#                 df_liquidity.set_value(index, 'TLB EOP', tlb_bop - tlb_amort)
#                 tlb_bop = tlb_eop
#             if row['TLC BOP'] <= 0:
#                 df_liquidity.set_value(index, 'TLC BOP', tlc_bop)
#                 tlc_eop =  tlc_bop + tlc_addl_borrow - tlc_amort - tlc_prepay
#                 df_liquidity.set_value(index, 'TLC EOP', tlc_bop)
#                 tlc_bop = tlc_eop
#
#     return df_liquidity


def build_libor(df_liquidity, df_libor_all, forecast_start, valuation_date):
    libor_list = [];
    for index, row in df_liquidity.iterrows():
        index = index.date();
        if index == date_utils.calc_month_end(forecast_start, 'date'):
            ''' first month does not use forward curve '''
            libor = get_smoothed_libor_spot_curve(df_libor_all, index, valuation_date);
            # sys.exit();
            # libor = get_libor(df_libor_all, index)
            libor_list.append([index, libor]);
            # df_liquidity.set_value(index, ['LIBOR'], libor)
        elif index > date_utils.calc_month_end(forecast_start, 'date'):
            """
                the libor in kean is already forward rates, we dont do calculation anymore
            """
            libor = get_smoothed_libor_spot_curve(df_libor_all, index, valuation_date);
            # df_liquidity.set_value(index, ['LIBOR'], libor)
            libor_list.append([index, libor]);



    for item in libor_list:
        # print (item[1]);
        df_liquidity.set_value(item[0],['LIBOR'],item[1]);

    return df_liquidity


def build_swap_rate(df_liquidity, df_swap, forecast_start):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) >= date_utils.calc_month_end(forecast_start, 'date'):
            month_start = date(index.year, index.month, 1)
            month_end = date(index.year, index.month, index.day)
            swap_balance = df_swap[month_start:month_end]['swap_balance'].sum()
            if swap_balance > 0:
                df_liquidity.set_value(index, ['Swap Avg Daily Balance'], swap_balance/index.day)
                swap_rate = df_swap[month_start:month_end]['calc_swap_rate'].sum() / swap_balance
                df_liquidity.set_value(index, ['Swap Fix Rate'], swap_rate + .045000)
            else:
                df_liquidity.set_value(index, ['Swap Avg Daily Balance'], 0)
                df_liquidity.set_value(index, ['Swap Fix Rate'], 0)
    return df_liquidity


def build_tlb_int_exp(df_liquidity, forecast_start):
    start = date_utils.calc_month_end(forecast_start, 'date')

    df_liquidity.loc[start:,['TLB Int Exp']] = df_liquidity['Swap Avg Daily Balance'] * df_liquidity['Swap Fix Rate'] \
            + (df_liquidity['TLB BOP']- df_liquidity['Swap Avg Daily Balance']) * df_liquidity['TLB Float Rate']
    df_liquidity.loc[start:,['TLB Int Exp']] = df_liquidity['TLB Int Exp'] * df_liquidity.index.day / YEAR_DAYS
    return df_liquidity


def build_tlc_int_exp(df_liquidity, forecast_start):
    start = date_utils.calc_month_end(forecast_start, 'date')
    df_liquidity.loc[start:,['TLC Int Exp']] = df_liquidity['TLC BOP'] * df_liquidity['TLC Float Rate'] * df_liquidity.index.day / YEAR_DAYS


def build_cash_actuals(df_liquidity, df_cash):
    ''' must set initial cash balance manually for now '''
    cash_bop = 56900000
    for index, row in df_cash.iterrows():
        df_liquidity.set_value(index, 'Cash BOP', cash_bop)
        cash_eop = row['Cash EOP']
        df_liquidity.set_value(index, 'Cash EOP', cash_eop)
        cash_bop = cash_eop
    return df_liquidity


def build_dsra(conn_ins, df_liquidity, scenario):
    df_dsra = db_controller_liquidity.get_actuals(conn_ins,'Deutsche Lightstone Debt Srvc Reserve Acct SC5173.4', 'ending_balance', 'DSRA EOP', scenario)
    for index, row in df_dsra.iterrows():
        dsra_eop = row['DSRA EOP']
        if date(index.year, index.month, index.day) == date(2017, 1, 31):
            ''' first bop = first eop'''
            df_liquidity.set_value(index, 'DSRA BOP', dsra_eop)
        else:
            df_liquidity.set_value(index, 'DSRA BOP', dsra_bop)
        df_liquidity.set_value(index, 'DSRA EOP', dsra_eop)
        dsra_bop = dsra_eop
    return df_liquidity


def build_distributions(conn_ins, df_liquidity, scenario):
    df_dist = db_controller_liquidity.get_actuals(conn_ins, 'Distribution', 'total_debit', 'Distributions', scenario)

    for i in range(0, len(df_dist)):
        print (df_dist.iloc[i]);

    for index, row in df_dist.iterrows():
        df_liquidity.set_value(index, 'Distributions', row['Distributions'])
    return df_liquidity


def build_other_cash_use(df_liquidity):
    ''' manual for now - need to identify in tb '''
    df_liquidity.set_value(date(2017,1,31), 'Other Cash Use', -4500000)
    df_liquidity.set_value(date(2017,3,31), 'Other Cash Use', -20790000)
    return df_liquidity


def build_change_work_cap(df_liquidity, forecast_start):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) < forecast_start:
            change_cash = row['Cash EOP'] - row['Cash BOP']
            activity_cash = row['EBITDA'] - row['Capex'] + row['Other Cash Use'] - row['TLB Int Exp'] - row['TLC Int Exp'] + row['TLB Change'] + row['DSRA Change'] - row['Distributions']
            change_work_cap = change_cash - activity_cash
        elif date(index.year, index.month, index.day) == date_utils.calc_month_end(forecast_start, 'date'):
            change_work_cap = -df_liquidity.loc[:forecast_start,['Change Work Cap']].sum() - 20000000
        else:
            change_work_cap = 0
        df_liquidity.set_value(index, 'Change Work Cap', change_work_cap)
    return df_liquidity


def build_int_exp_actual(df_liquidity):
    ''' manaually input for now '''
    df_liquidity.set_value(date(2017,1,31), 'TLB Int Exp', 0)
    df_liquidity.set_value(date(2017,2,28), 'TLB Int Exp', 1015746.25)
    df_liquidity.set_value(date(2017,3,31), 'TLB Int Exp', 17067021.5)
    df_liquidity.set_value(date(2017,4,30), 'TLB Int Exp', 11012419.96)
    df_liquidity.set_value(date(2017,5,31), 'TLB Int Exp', 9763733.48)
    df_liquidity.set_value(date(2017,6,30), 'TLB Int Exp', 9248754.57)
    df_liquidity.set_value(date(2017,7,31), 'TLB Int Exp', 8406426.53)
    return df_liquidity


def build_tax_depreciation(conn_ins, forecast_end, scenario, version):
    entities = {'Gavin':[600000000, 0], 'Waterford':[550000000, 0], 'Lawrenceburg': [590000000, 0], 'Darby': [150000000, 0], 'HoldCo': [151622000, 0]}
    entities_term = {'Gavin':28, 'Waterford':28, 'Lawrenceburg': 28, 'Darby': 20, 'HoldCo': 20}
    entities_principle_allo = {'Gavin':600000000, 'Waterford':550000000, 'Lawrenceburg': 590000000, 'Darby': 150000000, 'HoldCo': 151622000}

    tax_dep = {2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0}
    entity_taxdep_result_list = [];
    current_year = 2017
    while current_year <= forecast_end.year:
        for entity in entities:
            old_tax_dep_rate = calc_tax_depreciation(entity, False)
            new_capex = db_controller_liquidity.get_new_capex(conn_ins, scenario, entity, current_year,version)
            entities[entity][0] += new_capex
            new_tax_dep_rate = calc_tax_depreciation(entity, True)
            tax_dep[current_year] += entities[entity][0] * new_tax_dep_rate + entities[entity][1] * old_tax_dep_rate
            # if entity == 'Gavin':
            #     print (entity, current_year, entities[entity][0] , new_tax_dep_rate , entities[entity][1] , old_tax_dep_rate,  entities[entity][0] * new_tax_dep_rate + entities[entity][1] * old_tax_dep_rate);
            entity_taxdep_result_list.append([current_year, entity,entities[entity][0], entities_term[entity], entities_principle_allo[entity] , new_capex, entities[entity][0] * new_tax_dep_rate, entities[entity][0] * new_tax_dep_rate + entities[entity][1] * old_tax_dep_rate]);
            entities[entity][1] += entities[entity][0]
            entities[entity][0] = 0


        current_year += 1

    # for item in [items for items in entity_taxdep_result_list if items[1]=='Gavin']:
    #     print (item);

    """ here we hard coded """
    global TAX_DEPRECIATION_RESULT;
    if TAX_DEPRECIATION_RESULT == []:
        TAX_DEPRECIATION_RESULT = entity_taxdep_result_list;
    # sys.exit();
    return tax_dep


def build_est_tax_dist(conn_ins,df_liquidity, forecast_start, forecast_end, scenario, version):
    ''' manually assign oid and deferred finance charge (dfc) based on actuals '''

    tax_dep_all = build_tax_depreciation(conn_ins,forecast_end, scenario, version)
    # print (tax_dep_all);
    print (forecast_start);
    current_year_begin = date(forecast_start.year, 1, 1)
    current_year_end = date(forecast_start.year, 12,31)

    df_liquidity.to_csv("temp_liquidity_df.csv");

    while current_year_end <= forecast_end:
        ebitda = df_liquidity[current_year_begin:current_year_end]['EBITDA'].sum()
        int_exp_cash = df_liquidity[current_year_begin:current_year_end]['Int Exp'].sum()
        int_exp_tax = int_exp_cash + OID + DFC
        tax_dep = tax_dep_all[current_year_end.year]
        taxable_income = ebitda - int_exp_tax - tax_dep
        tax = max(taxable_income * ETR, 0)
        print ("current_year_end: ",current_year_end, "EBT: ", tax);

        if current_year_end == date(forecast_start.year, 12, 31):
            if forecast_start.month <= 3:
                df_liquidity.set_value(date(current_year_end.year, 3, 31),'Distributions', tax*0.2623)
                df_liquidity.set_value(date(current_year_end.year, 6, 30),'Distributions', tax*0.2459)
                df_liquidity.set_value(date(current_year_end.year, 9, 30),'Distributions', tax*0.2459)
                df_liquidity.set_value(date(current_year_end.year, 12, 31),'Distributions', tax*0.2459)
            elif forecast_start.month <= 6:
                df_liquidity.set_value(date(current_year_end.year, 6, 30),'Distributions', tax*0.2459)
                df_liquidity.set_value(date(current_year_end.year, 9, 30),'Distributions', tax*0.2459)
                df_liquidity.set_value(date(current_year_end.year, 12, 31),'Distributions', tax*0.2459)
            elif forecast_start.month <= 9:
                df_liquidity.set_value(date(current_year_end.year, 9, 30),'Distributions', tax*0.2459)
                df_liquidity.set_value(date(current_year_end.year, 12, 31),'Distributions', tax*0.2459)
            else:
                df_liquidity.set_value(date(current_year_end.year, 12, 31),'Distributions', tax*0.2459)
        else:
            df_liquidity.set_value(date(current_year_end.year, 3, 31),'Distributions', tax*0.2623)
            df_liquidity.set_value(date(current_year_end.year, 6, 30),'Distributions', tax*0.2459)
            df_liquidity.set_value(date(current_year_end.year, 9, 30),'Distributions', tax*0.2459)
            df_liquidity.set_value(date(current_year_end.year, 12, 31),'Distributions', tax*0.2459)
        current_year_end = date(current_year_end.year+1, 12, 31)
        current_year_begin = date(current_year_begin.year+1, 1, 1)


    # print (tax_dep_all);


    return df_liquidity


def build_tlb_bop_eop(df_liquidity):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) > date(2017, 1, 31):
            df_liquidity.set_value(index, 'Cash BOP', cash_bop)
            cash_eop = cash_bop + row['EBITDA'] - row['Capex'] + row['Other Cash Use'] - row['TLB Int Exp'] - row['TLC Int Exp'] \
                + row['TLB Change'] + row['DSRA Change'] - row['Distributions'] + row['Change Work Cap']
            df_liquidity.set_value(index, 'Cash EOP', cash_eop)
        cash_bop = row['Cash EOP']
    return df_liquidity


def search_for_prepay(df_liquidity, forecast_start, MIN_CASH):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) >= forecast_start:
            if index.month % 3 == 0:
                if row['Cash EOP'] > MIN_CASH:
                    prepay = math.ceil(row['Cash EOP'] - MIN_CASH)
                    df_liquidity.set_value(index, 'TLB Prepay', prepay)
                    break
    return df_liquidity


def recalc_tlb_amort(df, forecast_start):
    for index, row in df.iterrows():
        if date(index.year, index.month, index.day) >= forecast_start:
            if index.month % 3 == 0:
                required_amort = calc_required_amort(df, 'Lightstone TLB', index)
                cum_prepay = df.loc[:index]['TLB Prepay'].sum()
                cum_amort = df.loc[:index]['TLB Amort'].sum()
                tlb_amort = max(min(1625000000*0.0025,required_amort-cum_prepay-cum_amort),0)
                df.set_value(index, ['TLB Amort'], tlb_amort)
    return df


def recalc_tlb_int_exp(df_liquidity, forecast_start):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) >= forecast_start:
            swap_int_exp = row['Swap Avg Daily Balance'] * row['Swap Fix Rate']
            float_int_exp = (row['TLB BOP'] - row['Swap Avg Daily Balance']) * row['TLB Float Rate']
            df_liquidity.set_value(index, 'TLB Int Exp', (swap_int_exp + float_int_exp) * index.day/YEAR_DAYS)
    return df_liquidity


def recalc_tlb(df_liquidity, forecast_start):
    for index, row in df_liquidity.iterrows():
        if date(index.year, index.month, index.day) >= forecast_start:
            df_liquidity.set_value(index, 'TLB BOP', tlb_bop);
            tlb_eop = tlb_bop + row['TLB Addl Borrow'] - row['TLB Amort'] - row['TLB Prepay']
            df_liquidity.set_value(index, 'TLB EOP', tlb_eop)
        tlb_bop = row['TLB EOP']
    df_liquidity['TLB Change'] = df_liquidity['TLB EOP'].diff()
    df_liquidity.set_value(date(2017, 1,31), 'TLB Change', 0)   #no diff for first entry
    return df_liquidity
