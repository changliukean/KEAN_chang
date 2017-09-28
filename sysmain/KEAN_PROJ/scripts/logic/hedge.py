from pathlib import Path;
import os
import sys


from datetime import date;
from datetime import datetime;
from calendar import monthrange;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_hedge;
import db_controller;








def get_specific_price(df, instrument_id, period):
    ''' pass the df from get_all_commodity_prices - order is instrument_id, period, price '''
    ''' cheat and allow broad range of instrument_ids to be passed then cleaned up '''
    instrument_id = 'AD Hub ATC - Monthly Strip' if instrument_id == 'AD Hub DA ATC' else instrument_id
    instrument_id = 'AD Hub On Peak - Monthly Strip' if instrument_id == 'AD Hub DA Peak' else instrument_id
    instrument_id = 'AD Hub On Peak - Monthly Strip' if instrument_id == 'AD Hub RT Peak' else instrument_id
    instrument_id = 'Tetco ELA - Monthly Strip' if instrument_id == 'Tetco ELA' else instrument_id
    #instrument_id = 'TGT Zone 1 - Monthly Strip' if instrument_id == '' else instrument_id


    price = df.loc[(df['instrument_id']==instrument_id) & (df['period']==period)]




    price = 0 if price.empty else price.iloc[0]['price']

    return price


def calc_monthly_cashflow(price_receive, price_pay, notional, frequency, period, df_hours_pjm, option = False):
    days = monthrange(period.year, period.month)[1]
    periods = 0;
    if option:
        periods = days if frequency == 'Daily' else df_hours_pjm.loc[df_hours_pjm['end_date']==period].iloc[0]['onpeak'];
    else:
        periods = days if frequency == 'Daily' else df_hours_pjm.loc[df_hours_pjm['end_date']==period].iloc[0]['flat'];
    cashflow = (price_receive - price_pay) * notional * periods

    return cashflow;



def process_hedge(conn_ins, company, scenario, upload_to_kean=False):
    ''' Need to develop flexible means of accomodating different instrument_id '''
    '''    e.g. AD Hub DA ATC vs AD Hub RT ATC vs AD Hub ATC - Monthly Strip '''


    month_number = date_utils.get_month_number(scenario.split(" ")[1]);

    month_number += 1;

    forecast_start = date(2017, month_number, 1)
    forecast_end = date(2021, 12, 31)

    df_hedges = db_controller_hedge.get_hedges(conn_ins, company, 'HoldCo', forecast_start, forecast_end)
    df_hedges = df_hedges.loc[df_hedges['trade_date']<forecast_start];
    df_all_prices = db_controller_hedge.get_all_commodity_prices(conn_ins, scenario)
    df_hours_pjm = db_controller_hedge.get_hours_pjm(conn_ins);


    ''' write results to financials '''
    upload_to_financials_hedge_list = [];
    loop_date = date_utils.calc_month_end(forecast_start, 'date')
    while loop_date <= forecast_end:
        sum_cashflow = 0.0
        for i, hedge in df_hedges.iterrows():
            if hedge.loc['date_start'] <= loop_date and hedge.loc['date_end'] >= loop_date:
                # print (hedge.loc['receive_index']);
                price_receive = hedge.loc['receive_value'] if hedge.loc['receive_index'] == 'fixed' else get_specific_price(df_all_prices, hedge.loc['receive_index'], loop_date)
                price_pay = hedge.loc['pay_value'] if hedge.loc['pay_index'] == 'fixed' else get_specific_price(df_all_prices, hedge.loc['pay_index'], loop_date)
                monthly_cashflow = 0.0;
                if hedge.loc['pay_index'] == 'AD Hub DA Peak':
                    monthly_cashflow = calc_monthly_cashflow(price_receive, price_pay, hedge.loc['notional'], hedge.loc['frequency'], loop_date, df_hours_pjm, option = True)
                else:
                    monthly_cashflow = calc_monthly_cashflow(price_receive, price_pay, hedge.loc['notional'], hedge.loc['frequency'], loop_date, df_hours_pjm)

                sum_cashflow += monthly_cashflow
                # print (hedge.loc['tid_kindle'], loop_date, monthly_cashflow, '          ' ,sum_cashflow);

        # print ("--------------------------------------------");

        """
            we can use db_controller to do the upload
            we should build the upload list to store hedge values
        """
        #load_hedges_financials('2017 June AMR', 'Lightstone', 'HoldCo', 'Hedge P&L', loop_date, '%.2f' % sum_cashflow)
        """ (company, entity, scenario, account, period, value, version) """
        upload_to_financials_hedge_list.append([company, 'HoldCo', scenario, 'Hedge P&L', str(loop_date), str('%.2f' % sum_cashflow)]);
        loop_date = date_utils.calc_next_month_end(loop_date, 'date')


    for item in upload_to_financials_hedge_list:
        print (item);
    if upload_to_kean:
        db_controller.upload_cal_results_to_financials(conn_ins, upload_to_financials_hedge_list, company, scenario);


    return df_hedges, df_all_prices, df_hours_pjm;
