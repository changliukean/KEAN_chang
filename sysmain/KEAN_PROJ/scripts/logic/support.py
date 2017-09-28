import sys;
import os;
from pathlib import Path;
import datetime;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_support;
import db_controller;

COMPANY_ENTITY_ORDER_DICT = {'Lightstone':{'Gavin':0,'Lawrenceburg':1,'Waterford':2,'Darby':3}}
NON_GAS_PLANTS_DICT = {'Lightstone':['Gavin']}


ACTUALS_FINANCIALS_FSLI_LIST = ['Energy Revenue','Delivered Fuel Expense'];
BUDGET_FINANCIALS_FSLI_LIST = ['Energy Revenue','Delivered Fuel Expense'];


def pxq_main(conn_ins, company, amr_scenario, amr_version, budget_scenario, budget_version):
    # print (company, scenario);
    print (company, amr_scenario, amr_version, budget_scenario, budget_version);

    current_month = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[0][-1];

    current_month_obj = datetime.datetime.strptime(current_month, '%Y-%m-%d').date();

    actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario);

    pxq_pnl_ready_list, on_off_peak_ratio_list = get_pxq_pnl_ready(conn_ins, company, amr_scenario, budget_scenario);

    pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df = prepare_pxq_data_mtd_ytd(conn_ins, company, amr_scenario, amr_version, budget_scenario, budget_version);

    pxq_mtd_ready_list = get_pxq_mtd_ready(company, current_month_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df);

    pxq_ytd_ready_list = get_pxq_ytd_ready(company, current_month_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df);

    pxq_forecast_ready_list = get_pxq_forecast_ready(company, current_month_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df);

    af_monthly_list, budget_monthly_list = get_monthly_data_ready(company, current_month_obj, estimate_month_dates_list, budget_month_dates_list, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df);

    return pxq_pnl_ready_list, pxq_mtd_ready_list, pxq_ytd_ready_list, pxq_forecast_ready_list, af_monthly_list, budget_monthly_list;



def get_monthly_data_ready(company, month_date_obj, estimate_month_dates_list, budget_month_dates_list, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df):
    af_monthly_list = [];
    budget_monthly_list = [];

    entity_list = list(set(list(pxq_budget_input_data_df['entity'])));
    entity_list.sort(key=lambda val:(COMPANY_ENTITY_ORDER_DICT[company][val]));

    for current_entity in entity_list:


        current_pxq_forecast_df = pxq_dispatch_df.loc[(pxq_dispatch_df['entity'] == current_entity) & (pxq_dispatch_df['period'] > month_date_obj) & (pxq_dispatch_df['period'] <= datetime.datetime.strptime(estimate_month_dates_list[-1],"%Y-%m-%d").date())];
        current_pxq_actual_df = pxq_input_data_df.loc[(pxq_input_data_df['entity'] == current_entity) & (pxq_input_data_df['period'] <= month_date_obj)];
        ###########################################################################
        ############   on peak gen

        actual_onpeak_gen_list = [0.0 for i in range(0, len(budget_month_dates_list)-len(estimate_month_dates_list))];

        forecast_onpeak_gen_df = current_pxq_forecast_df.loc[(current_pxq_forecast_df['fsli'] == 'On-Peak Generation')][['value','period']];

        forecast_onpeak_gen_list = [];
        for i in range(0, len(forecast_onpeak_gen_df)):
            # print (forecast_onpeak_gen_df.iloc[i]);
            forecast_onpeak_gen_list.append([forecast_onpeak_gen_df.iloc[i]['value'],forecast_onpeak_gen_df.iloc[i]['period']]);

        # for item in forecast_onpeak_gen_list:
            # print (item);

        current_onpeak_gen_list = [current_entity, 'On Peak Generation'] + actual_onpeak_gen_list + list(list(zip(*(sorted(forecast_onpeak_gen_list, key = lambda x: (x[1])))))[0]);

        # print (current_onpeak_gen_list);

        ###########################################################################
        ############   off peak gen

        actual_offpeak_gen_list = [0.0 for i in range(0, len(budget_month_dates_list)-len(estimate_month_dates_list))];

        forecast_offpeak_gen_df = current_pxq_forecast_df.loc[(current_pxq_forecast_df['fsli'] == 'Off-Peak Generation')][['value','period']];


        forecast_offpeak_gen_list = [];
        for i in range(0, len(forecast_offpeak_gen_df)):
            forecast_offpeak_gen_list.append([forecast_offpeak_gen_df.iloc[i]['value'],forecast_offpeak_gen_df.iloc[i]['period']]);


        current_offpeak_gen_list = [current_entity, 'Off Peak Generation'] + actual_offpeak_gen_list + list(list(zip(*(sorted(forecast_offpeak_gen_list, key = lambda x: (x[1])))))[0]);

        ###########################################################################
        ############   on peak revenue

        actual_onpeak_rev_list = [0.0 for i in range(0, len(budget_month_dates_list)-len(estimate_month_dates_list))];

        forecast_onpeak_price_df = current_pxq_forecast_df.loc[ (current_pxq_forecast_df['fsli'] == 'Realized On-Peak Power Price')][['value','period']];


        forecast_onpeak_rev_list = [];
        for i in range(0, len(forecast_onpeak_price_df)):
            forecast_onpeak_rev_list.append([forecast_onpeak_price_df.iloc[i]['value'] * forecast_onpeak_gen_df.loc[forecast_onpeak_gen_df['period'] ==  forecast_onpeak_price_df.iloc[i]['period']].iloc[0]['value'], forecast_onpeak_price_df.iloc[i]['period']]);


        current_onpeak_rev_list = [current_entity, 'On Peak Revenue'] + actual_onpeak_rev_list + list(list(zip(*(sorted(forecast_onpeak_rev_list, key = lambda x: (x[1])))))[0]);

        ###########################################################################
        ############   off peak revenue

        actual_offpeak_rev_list = [0.0 for i in range(0, len(budget_month_dates_list)-len(estimate_month_dates_list))];

        forecast_offpeak_price_df = current_pxq_forecast_df.loc[(current_pxq_forecast_df['fsli'] == 'Realized Off-Peak Power Price')][['value','period']];


        forecast_offpeak_rev_list = [];
        for i in range(0, len(forecast_offpeak_price_df)):
            forecast_offpeak_rev_list.append([forecast_offpeak_price_df.iloc[i]['value'] * forecast_offpeak_gen_df.loc[forecast_offpeak_gen_df['period'] ==  forecast_offpeak_price_df.iloc[i]['period']].iloc[0]['value'], forecast_offpeak_price_df.iloc[i]['period']]);


        current_offpeak_rev_list = [current_entity, 'Off Peak Revenue'] + actual_offpeak_rev_list + list(list(zip(*(sorted(forecast_offpeak_rev_list, key = lambda x: (x[1])))))[0]);

        # print (current_offpeak_rev_list);

        ###########################################################################
        ############   delivered fuel
        actual_delivered_fuel_df = current_pxq_actual_df.loc[(current_pxq_actual_df['data_source'] == 'A+F') & (current_pxq_actual_df['input_title'] == 'Delivered Fuel')][['value','period']];


        actual_delivered_fuel_list = [];
        for i in range(0, len(actual_delivered_fuel_df)):
            actual_delivered_fuel_list.append([actual_delivered_fuel_df.iloc[i]['value'], actual_delivered_fuel_df.iloc[i]['period']]);


        current_actual_delivered_fuel_list = list(list(zip(*(sorted(actual_delivered_fuel_list, key = lambda x: (x[1])))))[0]);





        forecast_delivered_fuel_df = current_pxq_forecast_df.loc[(current_pxq_forecast_df['fsli'] == 'Delivered Fuel Cost')][['value','period']];
        forecast_fuel_burn_df = current_pxq_forecast_df.loc[(current_pxq_forecast_df['fsli'] == 'Fossil Fuel Consumed')][['value','period']];



        forecast_delivered_fuel_list = [];
        for i in range(0, len(forecast_delivered_fuel_df)):
            forecast_delivered_fuel_list.append([-0.001 * forecast_delivered_fuel_df.iloc[i]['value'] * forecast_fuel_burn_df.loc[forecast_fuel_burn_df['period'] == forecast_delivered_fuel_df.iloc[i]['period']].iloc[0]['value'], forecast_delivered_fuel_df.iloc[i]['period']]);


        current_delivered_fuel_list = [current_entity, 'Delivered Fuel Expense'] + current_actual_delivered_fuel_list + list(list(zip(*(sorted(forecast_delivered_fuel_list, key = lambda x: (x[1])))))[0]);


        ###########################################################################
        ############    fuel burn

        actual_fuel_burn_df = current_pxq_actual_df.loc[(current_pxq_actual_df['data_source'] == 'A+F') & (current_pxq_actual_df['input_title'] == 'Fuel Burn')][['value','period']];


        actual_fuel_burn_list = [];
        for i in range(0, len(actual_fuel_burn_df)):
            actual_fuel_burn_list.append([actual_fuel_burn_df.iloc[i]['value'], actual_fuel_burn_df.iloc[i]['period']]);


        current_actual_fuel_burn_list = list(list(zip(*(sorted(actual_fuel_burn_list, key = lambda x: (x[1])))))[0]);



        forecast_fuel_burn_list = [];
        for i in range(0, len(forecast_fuel_burn_df)):
            forecast_fuel_burn_list.append([0.001 * forecast_fuel_burn_df.iloc[i]['value'], forecast_fuel_burn_df.iloc[i]['period']]);


        current_fuel_burn_list = [current_entity, 'Fuel Burn'] + current_actual_fuel_burn_list + list(list(zip(*(sorted(forecast_fuel_burn_list, key = lambda x: (x[1])))))[0]);




        # print (current_onpeak_gen_list);
        # print (current_offpeak_gen_list);
        # print (current_onpeak_rev_list);
        # print (current_offpeak_rev_list);
        # print (current_delivered_fuel_list);
        # print (current_fuel_burn_list);

        current_total_gen_list = [current_entity,'Total Generation'] + list(current_pxq_actual_df.loc[(current_pxq_actual_df['data_source'] == 'A+F') & (current_pxq_actual_df['input_title'] == 'Total Generation')]['value']) + [current_onpeak_gen_list[i] + current_offpeak_gen_list[i] for i in range(2+len(budget_month_dates_list)-len(estimate_month_dates_list), len(current_onpeak_gen_list))];
        current_total_rev_list = [current_entity, 'Total Revenue'] + list(current_pxq_actual_df.loc[(current_pxq_actual_df['data_source'] == 'A+F') & (current_pxq_actual_df['input_title'] == 'Total Revenue')]['value']) + [current_onpeak_rev_list[i] + current_offpeak_rev_list[i] for i in range(2+len(budget_month_dates_list)-len(estimate_month_dates_list), len(current_onpeak_rev_list))];

        af_monthly_list.append([current_onpeak_gen_list, current_offpeak_gen_list, current_total_gen_list, current_onpeak_rev_list, current_offpeak_rev_list, current_total_rev_list, current_delivered_fuel_list, current_fuel_burn_list]);

        # sys.exit();


    for current_entity in entity_list:

        current_pxq_budget_df = pxq_budget_input_data_df.loc[(pxq_budget_input_data_df['entity'] == current_entity) & (pxq_budget_input_data_df['period'] >= datetime.datetime.strptime(budget_month_dates_list[0],"%Y-%m-%d").date()) & (pxq_budget_input_data_df['period'] <= datetime.datetime.strptime(estimate_month_dates_list[-1],"%Y-%m-%d").date())];

        ###########################################################################
        ############   on peak gen
        budget_onpeak_gen_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'On-Peak Generation')][['value','period']];

        budget_onpeak_gen_list = [];
        for i in range(0, len(budget_onpeak_gen_df)):
            # print (forecast_onpeak_gen_df.iloc[i]);
            budget_onpeak_gen_list.append([budget_onpeak_gen_df.iloc[i]['value'],budget_onpeak_gen_df.iloc[i]['period']]);

        current_onpeak_gen_list = [current_entity, 'On Peak Generation'] + list(list(zip(*(sorted(budget_onpeak_gen_list, key = lambda x: (x[1])))))[0]);

        ###########################################################################
        ############   off peak gen

        budget_offpeak_gen_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'Off-Peak Generation')][['value','period']];

        budget_offpeak_gen_list = [];
        for i in range(0, len(budget_offpeak_gen_df)):
            # print (forecast_onpeak_gen_df.iloc[i]);
            budget_offpeak_gen_list.append([budget_offpeak_gen_df.iloc[i]['value'],budget_offpeak_gen_df.iloc[i]['period']]);

        current_offpeak_gen_list = [current_entity, 'Off Peak Generation'] + list(list(zip(*(sorted(budget_offpeak_gen_list, key = lambda x: (x[1])))))[0]);

        ###########################################################################
        ############   on peak rev

        budget_onpeak_price_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'Realized On-Peak Power Price')][['value','period']];


        budget_onpeak_rev_list = [];
        for i in range(0, len(budget_onpeak_price_df)):
            budget_onpeak_rev_list.append([budget_onpeak_price_df.iloc[i]['value'] * budget_onpeak_gen_df.loc[budget_onpeak_gen_df['period'] == budget_onpeak_price_df.iloc[i]['period']].iloc[0]['value'],budget_onpeak_price_df.iloc[i]['period']]);

        current_onpeak_rev_list = [current_entity, 'On Peak Revenue'] + list(list(zip(*(sorted(budget_onpeak_rev_list, key = lambda x: (x[1])))))[0]);


        ###########################################################################
        ############   off peak rev

        budget_offpeak_price_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'Realized Off-Peak Power Price')][['value','period']];


        budget_offpeak_rev_list = [];
        for i in range(0, len(budget_offpeak_price_df)):
            budget_offpeak_rev_list.append([budget_offpeak_price_df.iloc[i]['value'] * budget_offpeak_gen_df.loc[budget_offpeak_gen_df['period'] == budget_offpeak_price_df.iloc[i]['period']].iloc[0]['value'],budget_offpeak_price_df.iloc[i]['period']]);

        current_offpeak_rev_list = [current_entity, 'Off Peak Revenue'] + list(list(zip(*(sorted(budget_offpeak_rev_list, key = lambda x: (x[1])))))[0]);


        ###########################################################################
        ############   delivered fuel expense

        budget_del_fuel_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'Delivered Fuel')][['value','period']];

        budget_del_fuel_list = [];
        for i in range(0, len(budget_del_fuel_df)):
            budget_del_fuel_list.append([0.001 * budget_del_fuel_df.iloc[i]['value'], budget_del_fuel_df.iloc[i]['period']]);

        current_del_fuel_list = [current_entity, 'Delivered Fuel Expense'] + list(list(zip(*(sorted(budget_del_fuel_list, key = lambda x: (x[1])))))[0]);


        ###########################################################################
        ############   fuel burn

        budget_fuel_burn_df = current_pxq_budget_df.loc[(current_pxq_budget_df['account_name'] == 'Fossil Fuel Consumed')][['value','period']];

        budget_fuel_burn_list = [];
        for i in range(0, len(budget_fuel_burn_df)):
            budget_fuel_burn_list.append([budget_fuel_burn_df.iloc[i]['value'], budget_fuel_burn_df.iloc[i]['period']]);

        current_fuel_burn_list = [current_entity, 'Fuel Burn'] + list(list(zip(*(sorted(budget_fuel_burn_list, key = lambda x: (x[1])))))[0]);


        current_total_gen_list = [current_entity,'Total Generation'] + [current_onpeak_gen_list[i] + current_offpeak_gen_list[i] for i in range(2, len(current_onpeak_gen_list))];
        current_total_rev_list = [current_entity, 'Total Revenue'] + [current_onpeak_rev_list[i] + current_offpeak_rev_list[i] for i in range(2, len(current_onpeak_rev_list))];


        budget_monthly_list.append([current_onpeak_gen_list, current_offpeak_gen_list, current_total_gen_list, current_onpeak_rev_list, current_offpeak_rev_list, current_total_rev_list, current_del_fuel_list, current_fuel_burn_list]);



    return af_monthly_list, budget_monthly_list;




def get_pxq_forecast_ready(company, month_date_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df):
    print ("------------------ forecast -----------------");
    pxq_forecast_ready_list = [];

    year_end_date_obj = datetime.datetime.strptime(str(month_date_obj).split(" ")[0].split("-")[0]+"-12-31", "%Y-%m-%d").date();

    print (year_end_date_obj);

    print (len(pxq_input_data_df), len(pxq_budget_input_data_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df), len(pxq_dispatch_df));

    pxq_financials_actuals_df = pxq_financials_actuals_df.loc[(pxq_financials_actuals_df['account'].isin(ACTUALS_FINANCIALS_FSLI_LIST)) & (pxq_financials_actuals_df['period'] > month_date_obj) & (pxq_financials_actuals_df['period'] <= year_end_date_obj)];
    pxq_financials_budget_df = pxq_financials_budget_df.loc[(pxq_financials_budget_df['account'].isin(BUDGET_FINANCIALS_FSLI_LIST)) & (pxq_financials_budget_df['period'] > month_date_obj) & (pxq_financials_budget_df['period'] <= year_end_date_obj)];
    pxq_input_data_df = pxq_input_data_df.loc[(pxq_input_data_df['period'] > month_date_obj) & (pxq_input_data_df['period'] <= year_end_date_obj)];
    pxq_budget_input_data_df = pxq_budget_input_data_df.loc[(pxq_budget_input_data_df['period'] > month_date_obj) & (pxq_budget_input_data_df['period'] <= year_end_date_obj)];
    pxq_dispatch_df = pxq_dispatch_df.loc[(pxq_dispatch_df['period'] > month_date_obj) & (pxq_dispatch_df['period'] <= year_end_date_obj)];

    print (len(pxq_input_data_df), len(pxq_budget_input_data_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df), len(pxq_dispatch_df));

    entity_list = list(set(list(pxq_budget_input_data_df['entity'])));

    entity_list.sort(key=lambda val:(COMPANY_ENTITY_ORDER_DICT[company][val]));



    ################################################################################################
    ################################################################################################
    ####    estimates part
    ################################################################################################
    ################################################################################################


    forecast_ready_list = [];

    for current_entity in entity_list:
        current_pxq_dispatch_df = pxq_dispatch_df.loc[pxq_dispatch_df['entity'] == current_entity];


        current_onpeak_gen = sum(list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'On-Peak Generation']['value']));
        current_offpeak_gen = sum(list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'Off-Peak Generation']['value']));

        current_onpeak_engrev = sum([gen * price for gen, price in zip(list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'On-Peak Generation']['value']),list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'Realized On-Peak Power Price']['value']))])
        current_offpeak_engrev = sum([gen * price for gen, price in zip(list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'Off-Peak Generation']['value']),list(current_pxq_dispatch_df.loc[current_pxq_dispatch_df['fsli'] == 'Realized Off-Peak Power Price']['value']))])


        current_total_engrev = current_onpeak_engrev + current_offpeak_engrev;
        current_onpeak_price = current_onpeak_engrev / current_onpeak_gen;
        current_offpeak_price = current_offpeak_engrev / current_offpeak_gen;

        forecast_ready_list.append([current_entity, current_onpeak_gen, current_offpeak_gen, current_onpeak_price, current_offpeak_price, current_onpeak_engrev, current_offpeak_engrev, current_total_engrev]);


    total_act_on_gen = sum(list(zip(*forecast_ready_list))[1]);
    total_act_off_gen = sum(list(zip(*forecast_ready_list))[2]);
    total_act_on_engrev = sum(list(zip(*forecast_ready_list))[5]);
    total_act_off_engrev = sum(list(zip(*forecast_ready_list))[6]);
    total_act_total_engrev = sum(list(zip(*forecast_ready_list))[7]);
    total_act_on_price = total_act_on_engrev / total_act_on_gen;
    total_act_off_price = total_act_off_engrev / total_act_off_gen;

    forecast_ready_list.append(['Total', total_act_on_gen, total_act_off_gen, total_act_on_price, total_act_off_price, total_act_on_engrev, total_act_off_engrev, total_act_total_engrev]);


    pxq_forecast_ready_list.append(forecast_ready_list);

    ################################################################################################
    ################################################################################################
    ####    budget part
    ################################################################################################
    ################################################################################################

    budget_ready_list = [];

    for current_entity in entity_list:
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];
        current_onpeak_gen_list = list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'On-Peak Generation']['value']);
        current_offpeak_gen_list = list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Off-Peak Generation']['value']);
        current_onpeak_price_list = list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Realized On-Peak Power Price']['value']);
        current_offpeak_price_list = list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Realized Off-Peak Power Price']['value']);

        current_onpeak_gen = sum(current_onpeak_gen_list);
        current_offpeak_gen = sum(current_offpeak_gen_list);
        current_onpeak_engrev = sum([gen * price for gen, price in zip(current_onpeak_gen_list,current_onpeak_price_list)]);
        current_offpeak_engrev = sum([gen * price for gen, price in zip(current_offpeak_gen_list,current_offpeak_price_list)])

        current_onpeak_price = current_onpeak_engrev / current_onpeak_gen;
        current_offpeak_price = current_offpeak_engrev / current_offpeak_gen;

        current_total_engrev = current_onpeak_engrev + current_offpeak_engrev;

        budget_ready_list.append([current_entity, current_onpeak_gen, current_offpeak_gen, current_onpeak_price, current_offpeak_price, current_onpeak_engrev, current_offpeak_engrev, current_total_engrev]);



    total_budget_on_gen = sum(list(zip(*budget_ready_list))[1]);
    total_budget_off_gen = sum(list(zip(*budget_ready_list))[2]);
    total_budget_on_engrev = sum(list(zip(*budget_ready_list))[5]);
    total_budget_off_engrev = sum(list(zip(*budget_ready_list))[6]);
    total_budget_total_engrev = sum(list(zip(*budget_ready_list))[7]);
    total_budget_on_price = total_budget_on_engrev / total_budget_on_gen;
    total_budget_off_price = total_budget_off_engrev / total_budget_off_gen;

    budget_ready_list.append(['Total', total_budget_on_gen, total_budget_off_gen, total_budget_on_price, total_budget_off_price, total_budget_on_engrev, total_budget_off_engrev, total_budget_total_engrev]);

    pxq_forecast_ready_list.append(budget_ready_list);

    ################################################################################################
    ################################################################################################
    ####    variance part
    ################################################################################################
    ################################################################################################

    variance_ready_list = [];

    for current_entity in entity_list+['Total']:
        forecast_row = [item for item in forecast_ready_list if item[0] == current_entity][0];
        budget_row = [item for item in budget_ready_list if item[0] == current_entity][0];
        temp_var_row = [];
        for i in range(0, len(forecast_row)):
            if i == 0:
                temp_var_row.append(forecast_row[i]);
            else:
                temp_var_row.append(forecast_row[i] - budget_row[i]);
        variance_ready_list.append(temp_var_row);

    pxq_forecast_ready_list.append(variance_ready_list);


    ################################################################################################
    ################################################################################################
    ####    pq analysis part
    ################################################################################################
    ################################################################################################

    pq_analysis_ready_list = [];

    for current_entity in entity_list:
        current_var_row = [item for item in variance_ready_list if item[0] == current_entity][0];
        current_budget_row = [item for item in budget_ready_list if item[0] == current_entity][0];
        current_forecast_row = [item for item in forecast_ready_list if item[0] == current_entity][0];
        current_on_price = current_var_row[3] * current_budget_row[1];
        current_off_price = current_var_row[4] * current_budget_row[2];
        current_on_quant = current_var_row[1] * current_forecast_row[3];
        current_off_quant = current_var_row[2] * current_forecast_row[4];

        current_price_total = current_on_price + current_off_price;
        current_quant_total = current_on_quant + current_off_quant;
        current_total = current_price_total + current_quant_total;

        pq_analysis_ready_list.append([current_entity, current_on_price, current_off_price, current_on_quant, current_off_quant, current_price_total, current_quant_total, current_total]);

    """ look how Pythonic I am !!!!!!!!!!!!!!!!!!!!!!!!!! """
    pq_sum_row = ['Total'] + [sum(item) for item in list(zip(*pq_analysis_ready_list))[1:]];

    pq_analysis_ready_list.append(pq_sum_row);

    pxq_forecast_ready_list.append(pq_analysis_ready_list);




    ################################################################################################
    ################################################################################################
    ####    delievered fuel expense part
    ################################################################################################
    ################################################################################################

    delivered_fuel_ready_list = [];

    for current_entity in entity_list:
        current_pxq_data_df = pxq_input_data_df.loc[pxq_input_data_df['entity'] == current_entity];
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];
        current_pxq_financials_actuals_df = pxq_financials_actuals_df.loc[pxq_financials_actuals_df['entity'] == current_entity];
        current_pxq_financials_budget_df = pxq_financials_budget_df.loc[pxq_financials_budget_df['entity'] == current_entity];
        act_fuel_burn = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Fuel Burn')]['value']));
        budget_fuel_burn = sum(list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Fossil Fuel Consumed']['value']));
        act_delivered_fuel = -sum(list(current_pxq_financials_actuals_df.loc[current_pxq_financials_actuals_df['account'] == 'Delivered Fuel Expense']['value']))/1000.0;
        budget_delieverd_fuel = -sum(list(current_pxq_financials_budget_df.loc[current_pxq_financials_budget_df['account'] == 'Delivered Fuel Expense']['value']))/1000.0;

        act_fuel_price = act_delivered_fuel / act_fuel_burn;
        budget_fuel_price = budget_delieverd_fuel / budget_fuel_burn;

        delta_fuel_burn = act_fuel_burn - budget_fuel_burn;
        delta_fuel_price = act_fuel_price - budget_fuel_price;

        pxq_price = act_fuel_price * delta_fuel_burn;
        pxq_quant = budget_fuel_burn * delta_fuel_price;
        pxq_total = pxq_price + pxq_quant;

        delivered_fuel_ready_list.append([current_entity, act_fuel_burn, act_fuel_price, budget_fuel_burn, budget_fuel_price, delta_fuel_burn, delta_fuel_price, pxq_price, pxq_quant, pxq_total, act_delivered_fuel, budget_delieverd_fuel]);



    total_act_fuel_burn = sum(list(zip(*delivered_fuel_ready_list))[1]);
    total_budget_fuel_burn = sum(list(zip(*delivered_fuel_ready_list))[3]);
    total_delta_fuel_burn = sum(list(zip(*delivered_fuel_ready_list))[5]);
    total_pxq_price = sum(list(zip(*delivered_fuel_ready_list))[7]);
    total_pxq_quant = sum(list(zip(*delivered_fuel_ready_list))[8]);
    total_pxq_total = sum(list(zip(*delivered_fuel_ready_list))[9]);
    total_act_delivered_fuel = sum(list(zip(*delivered_fuel_ready_list))[10]);
    total_budget_delivered_fuel = sum(list(zip(*delivered_fuel_ready_list))[11]);

    total_act_price = total_act_delivered_fuel / total_act_fuel_burn;
    total_budget_price = total_budget_delivered_fuel / total_budget_fuel_burn;

    total_delta_price = total_act_price - total_budget_price;

    delivered_fuel_ready_list.append(['Total', total_act_fuel_burn, total_act_price, total_budget_fuel_burn, total_budget_price, total_delta_fuel_burn, total_delta_price, total_pxq_price, total_pxq_quant, total_pxq_total, total_act_delivered_fuel, total_budget_delivered_fuel]);

    pxq_forecast_ready_list.append(delivered_fuel_ready_list);

    return pxq_forecast_ready_list;




def get_pxq_ytd_ready(company, month_date_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df):
    print ("---------------- ytd ----------------");

    pxq_ytd_ready_list = [];

    pxq_ytd_act_budget_list = [];

    # print (month_date_obj);

    print (len(pxq_input_data_df), len(pxq_budget_input_data_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df));

    pxq_financials_actuals_df = pxq_financials_actuals_df.loc[(pxq_financials_actuals_df['account'].isin(ACTUALS_FINANCIALS_FSLI_LIST)) & (pxq_financials_actuals_df['period'] <= month_date_obj)];
    pxq_financials_budget_df = pxq_financials_budget_df.loc[(pxq_financials_budget_df['account'].isin(BUDGET_FINANCIALS_FSLI_LIST)) & (pxq_financials_budget_df['period'] <= month_date_obj)];

    pxq_input_data_df = pxq_input_data_df.loc[pxq_input_data_df['period'] <= month_date_obj];
    pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['period'] <= month_date_obj];

    ################################################################################################
    ################################################################################################
    ####    actuals and budget part
    ################################################################################################
    ################################################################################################

    entity_list = list(set(list(pxq_budget_input_data_df['entity'])));

    entity_list.sort(key=lambda val:(COMPANY_ENTITY_ORDER_DICT[company][val]));

    # for item in entity_list:
    #     print (item);


    print (len(pxq_input_data_df), len(pxq_budget_input_data_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df));


    for current_entity in entity_list:
        current_pxq_data_df = pxq_input_data_df.loc[pxq_input_data_df['entity'] == current_entity];
        current_pxq_financials_actuals_df = pxq_financials_actuals_df.loc[pxq_financials_actuals_df['entity'] == current_entity];
        current_pxq_financials_budget_df = pxq_financials_budget_df.loc[pxq_financials_budget_df['entity'] == current_entity];
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];



        act_total_gen = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Total Generation')]['value']));
        act_total_engrev = sum(list(current_pxq_financials_actuals_df.loc[current_pxq_financials_actuals_df['account'] == 'Energy Revenue']['value']))/1000.0;
        # print (list(current_pxq_financials_actuals_df.loc[current_pxq_financials_actuals_df['account'] == 'Energy Revenue']['value']));
        # print (current_entity, act_total_engrev);


        act_total_price = act_total_engrev / act_total_gen;
        budget_onpeak_gen = sum(list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'On-Peak Generation']['value']));
        budget_offpeak_gen = sum(list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Off-Peak Generation']['value']));
        budget_total_gen = budget_onpeak_gen + budget_offpeak_gen;
        budget_total_engrev = sum(list(current_pxq_financials_budget_df.loc[current_pxq_financials_budget_df['account'] == 'Energy Revenue']['value']))/1000.0;

        budget_onpeak_engrev = 0;
        budget_offpeak_engrev = 0;

        ytd_date_list = list(set(list(current_pxq_data_df['period'])));
        ytd_date_list = sorted(ytd_date_list);

        for month_end in ytd_date_list:
            if str(month_end).split(" ")[0] != '2017-01-31':
                onpeak_gen = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'On-Peak Generation')].iloc[0]['value'];
                onpeak_price = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'Realized On-Peak Power Price')].iloc[0]['value']
                offpeak_gen = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'Off-Peak Generation')].iloc[0]['value'];
                offpeak_price = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'Realized Off-Peak Power Price')].iloc[0]['value'];



                onpeak_engrev = onpeak_gen * onpeak_price * 1000;
                offpeak_engrev = offpeak_gen * offpeak_price * 1000;
                total_engrev = onpeak_engrev + offpeak_engrev;
                budget_onpeak_engrev += onpeak_engrev;
                budget_offpeak_engrev += offpeak_engrev;
                # print (budget_offpeak_engrev);
                # print (current_entity, month_end, onpeak_gen, offpeak_gen, total_engrev, onpeak_engrev, offpeak_engrev);
            else:
                onpeak_gen = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'On-Peak Generation')].iloc[0]['value'];
                offpeak_gen = current_pxq_budget_input_data_df.loc[(current_pxq_budget_input_data_df['period'] == month_end) & (current_pxq_budget_input_data_df['account_name'] == 'Off-Peak Generation')].iloc[0]['value'];
                total_engrev = current_pxq_financials_budget_df.loc[(current_pxq_financials_budget_df['account'] == 'Energy Revenue') & (current_pxq_financials_budget_df['period'] == month_end)].iloc[0]['value'];

                # print (current_entity, month_end, onpeak_gen, offpeak_gen, total_engrev)

                onpeak_engrev = 0
                offpeak_engrev = 0;
                if onpeak_gen + offpeak_gen > 1:
                    onpeak_engrev = onpeak_gen/ (onpeak_gen + offpeak_gen) * total_engrev;
                    offpeak_engrev = offpeak_gen/ (onpeak_gen + offpeak_gen) * total_engrev;
                budget_onpeak_engrev += onpeak_engrev;
                budget_offpeak_engrev += offpeak_engrev;
                # print (budget_offpeak_engrev);
                # print (current_entity, month_end, onpeak_gen, offpeak_gen, total_engrev, onpeak_engrev, offpeak_engrev);

        budget_onpeak_engrev = budget_onpeak_engrev / 1000.0;
        budget_offpeak_engrev = budget_offpeak_engrev / 1000.0;

        budget_onpeak_realized_price = budget_onpeak_engrev / budget_onpeak_gen ;
        budget_offpeak_realized_price = budget_offpeak_engrev / budget_offpeak_gen ;
        budget_atc_price = budget_total_engrev / budget_total_gen;


        # print (current_entity, act_total_gen, act_total_price ,act_total_engrev, budget_onpeak_gen, budget_offpeak_gen, budget_total_gen, budget_onpeak_realized_price, budget_offpeak_realized_price, budget_atc_price, budget_onpeak_engrev, budget_offpeak_engrev, budget_total_engrev);
        pxq_ytd_act_budget_list.append([current_entity, act_total_gen, act_total_price ,act_total_engrev, budget_onpeak_gen, budget_offpeak_gen, budget_total_gen, budget_onpeak_realized_price, budget_offpeak_realized_price, budget_atc_price, budget_onpeak_engrev, budget_offpeak_engrev, budget_total_engrev]);

    total_act_gen = sum(list(zip(*pxq_ytd_act_budget_list))[1]);
    total_act_engrev = sum(list(zip(*pxq_ytd_act_budget_list))[3]);
    total_act_price = total_act_engrev / total_act_gen;

    total_budget_onpeak_gen = sum(list(zip(*pxq_ytd_act_budget_list))[4]);
    total_budget_offpeak_gen = sum(list(zip(*pxq_ytd_act_budget_list))[5]);
    total_budget_total_gen = sum(list(zip(*pxq_ytd_act_budget_list))[6]);

    total_onpeak_engrev = sum(list(zip(*pxq_ytd_act_budget_list))[10]);
    total_offpeak_engrev = sum(list(zip(*pxq_ytd_act_budget_list))[11]);
    total_total_engrev = sum(list(zip(*pxq_ytd_act_budget_list))[12]);

    total_act_price = total_act_engrev / total_act_gen;
    total_budget_on_price = total_onpeak_engrev / total_budget_onpeak_gen;
    total_budget_off_price = total_offpeak_engrev / total_budget_offpeak_gen;
    total_budget_atc_price = total_total_engrev / total_budget_total_gen;

    pxq_ytd_act_budget_list.append(['Total', total_act_gen, total_act_price, total_act_engrev, total_budget_onpeak_gen, total_budget_offpeak_gen, total_budget_total_gen, total_budget_on_price, total_budget_off_price, total_budget_atc_price, total_onpeak_engrev, total_offpeak_engrev, total_total_engrev])



    pxq_ytd_ready_list.append(pxq_ytd_act_budget_list);

    ################################################################################################
    ################################################################################################
    ####    Variance and pq analysis part
    ################################################################################################
    ################################################################################################

    pxq_ytd_var_pqa_list = [];

    for current_entity in entity_list:
        var_gen = [item[1]-item[6] for item in pxq_ytd_act_budget_list if item[0] == current_entity][0];
        var_realized_price = [item[2]-item[9] for item in pxq_ytd_act_budget_list if item[0] == current_entity][0];
        var_engrev = [item[3] - item[12] for item in pxq_ytd_act_budget_list if item[0] == current_entity][0];

        pq_price = [item[6] * var_realized_price for item in pxq_ytd_act_budget_list if item[0] == current_entity][0];
        pq_quantity = [item[2] * var_gen for item in pxq_ytd_act_budget_list if item[0] == current_entity][0];
        pq_total = pq_price + pq_quantity;

        pxq_ytd_var_pqa_list.append([current_entity, var_gen, var_realized_price, var_engrev, pq_price, pq_quantity, pq_total]);


    total_var_gen = sum(list(zip(*pxq_ytd_var_pqa_list))[1]);

    total_var_engrev = sum(list(zip(*pxq_ytd_var_pqa_list))[3]);
    total_var_price = pxq_ytd_act_budget_list[-1][2] - pxq_ytd_act_budget_list[-1][9];

    total_pxq_price = sum(list(zip(*pxq_ytd_var_pqa_list))[4]);
    total_pxq_quant = sum(list(zip(*pxq_ytd_var_pqa_list))[5]);
    total_pxq_total = sum(list(zip(*pxq_ytd_var_pqa_list))[6]);


    pxq_ytd_var_pqa_list.append(['Total', total_var_gen, total_var_price, total_var_engrev, total_pxq_price, total_pxq_quant, total_pxq_total]);

    pxq_ytd_ready_list.append(pxq_ytd_var_pqa_list);




    ################################################################################################
    ################################################################################################
    ####    delivered fuel expense pq analysis part
    ################################################################################################
    ################################################################################################


    del_fuel_exp_list = [];

    for current_entity in entity_list:
        current_pxq_data_df = pxq_input_data_df.loc[pxq_input_data_df['entity'] == current_entity];
        current_pxq_financials_actuals_df = pxq_financials_actuals_df.loc[pxq_financials_actuals_df['entity'] == current_entity];
        current_pxq_financials_budget_df = pxq_financials_budget_df.loc[pxq_financials_budget_df['entity'] == current_entity];
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];


        act_fuel_expense = -sum(list(current_pxq_financials_actuals_df.loc[current_pxq_financials_actuals_df['account'] == 'Delivered Fuel Expense']['value']))/1000.0;
        budget_fuel_expense = -sum(list(current_pxq_financials_budget_df.loc[current_pxq_financials_budget_df['account'] == 'Delivered Fuel Expense']['value']))/1000.0;

        act_fuel_burn = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['input_title'] == 'Fuel Burn') & (current_pxq_data_df['data_source'] == 'A+F')]['value']));
        act_fuel_price = act_fuel_expense / act_fuel_burn;

        budget_fuel_burn = sum(list(current_pxq_budget_input_data_df.loc[current_pxq_budget_input_data_df['account_name'] == 'Fossil Fuel Consumed']['value']));
        budget_fuel_price = budget_fuel_expense / budget_fuel_burn;

        delta_fuel_burn = act_fuel_burn - budget_fuel_burn;
        delta_fuel_price = act_fuel_price - budget_fuel_price;

        pxq_price = act_fuel_price * delta_fuel_burn;
        pxq_quantity = budget_fuel_burn * delta_fuel_price;
        pxq_total = pxq_price + pxq_quantity;

        del_fuel_exp_list.append([current_entity, act_fuel_burn, act_fuel_price, budget_fuel_burn, budget_fuel_price, delta_fuel_burn, delta_fuel_price, pxq_price, pxq_quantity, pxq_total, act_fuel_expense, budget_fuel_expense]);




    total_act_fuel_burn = sum(list(zip(*del_fuel_exp_list))[1]);
    total_budget_fuel_burn = sum(list(zip(*del_fuel_exp_list))[3]);
    total_delta_fuel_burn = sum(list(zip(*del_fuel_exp_list))[5]);

    total_pxq_price = sum(list(zip(*del_fuel_exp_list))[7]);
    total_pxq_quant = sum(list(zip(*del_fuel_exp_list))[8]);
    total_pxq_total = sum(list(zip(*del_fuel_exp_list))[9]);

    total_act_delivered_fuel = sum(list(zip(*del_fuel_exp_list))[10]);
    total_budget_delivered_fuel = sum(list(zip(*del_fuel_exp_list))[11]);

    total_act_fuel_price = total_act_delivered_fuel / total_act_fuel_burn;
    total_budget_fuel_price = total_budget_delivered_fuel / total_budget_fuel_burn;

    total_delta_price = total_act_fuel_price - total_budget_fuel_price;

    del_fuel_exp_list.append(['Total', total_act_fuel_burn, total_act_fuel_price, total_budget_fuel_burn, total_budget_fuel_price, total_delta_fuel_burn, total_delta_price, total_pxq_price, total_pxq_quant, total_pxq_total, total_act_delivered_fuel, total_budget_delivered_fuel]);

    pxq_ytd_ready_list.append(del_fuel_exp_list);


    ################################################################################################
    ################################################################################################
    ####   capacity factor part
    ################################################################################################
    ################################################################################################
    capacity_factor_list = [];

    for current_entity in entity_list:
        current_pxq_data_df = pxq_input_data_df.loc[pxq_input_data_df['entity'] == current_entity];
        current_pxq_financials_actuals_df = pxq_financials_actuals_df.loc[pxq_financials_actuals_df['entity'] == current_entity];
        current_pxq_financials_budget_df = pxq_financials_budget_df.loc[pxq_financials_budget_df['entity'] == current_entity];
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];

        first_month_date = datetime.datetime.strptime("2017-01-31","%Y-%m-%d").date();

        capacity_value = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Budget Capacity') & (current_pxq_data_df['period'] > first_month_date)]['value'])) / (len(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Budget Capacity') & (current_pxq_data_df['period'] > first_month_date)]['value'])));
        period_hours_value = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Period Hours')]['value']));
        generation_value = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'Total Generation')]['value']));
        capacity_factor = generation_value / (capacity_value * period_hours_value) * 1000.0;

        capacity_factor_list.append([current_entity, capacity_value, period_hours_value, generation_value, capacity_factor]);

    if company in NON_GAS_PLANTS_DICT:
        temp_capacity_factor_list = [];

        non_gas_plant_list = NON_GAS_PLANTS_DICT[company];
        gas_plants_list = list(set(entity_list) - set(non_gas_plant_list));
        current_entity = 'Gas Plants';
        current_capacity = sum([item[1] for item in capacity_factor_list if item[0] in gas_plants_list]);
        current_period_hours = [item[2] for item in capacity_factor_list if item[0] in gas_plants_list][-1];
        current_generation = sum([item[3] for item in capacity_factor_list if item[0] in gas_plants_list]);
        current_capacity_factor = current_generation / (current_period_hours * current_capacity) * 1000.0;
        temp_capacity_factor_list.append([current_entity, current_capacity, current_period_hours, current_generation, current_capacity_factor]);

        current_entity = non_gas_plant_list[0];
        current_capacity = sum([item[1] for item in capacity_factor_list if item[0] not in gas_plants_list]);
        current_period_hours = [item[2] for item in capacity_factor_list if item[0] not in gas_plants_list][-1];
        current_generation = sum([item[3] for item in capacity_factor_list if item[0] not in gas_plants_list]);
        current_capacity_factor = current_generation / (current_period_hours * current_capacity) * 1000.0;
        temp_capacity_factor_list.append([current_entity, current_capacity, current_period_hours, current_generation, current_capacity_factor]);

        current_entity = company;
        current_capacity = sum([item[1] for item in capacity_factor_list]);
        current_period_hours = [item[2] for item in capacity_factor_list][-1];
        current_generation = sum([item[3] for item in capacity_factor_list]);
        current_capacity_factor = current_generation / (current_period_hours * current_capacity) * 1000.0;
        temp_capacity_factor_list.append([current_entity, current_capacity, current_period_hours, current_generation, current_capacity_factor]);

        capacity_factor_list = capacity_factor_list + temp_capacity_factor_list;


    pxq_ytd_ready_list.append(capacity_factor_list);


    ################################################################################################
    ################################################################################################
    ####    EAF part
    ################################################################################################
    ################################################################################################

    eaf_list = [];

    for current_entity in entity_list:
        current_pxq_data_df = pxq_input_data_df.loc[pxq_input_data_df['entity'] == current_entity];
        current_pxq_financials_actuals_df = pxq_financials_actuals_df.loc[pxq_financials_actuals_df['entity'] == current_entity];
        current_pxq_financials_budget_df = pxq_financials_budget_df.loc[pxq_financials_budget_df['entity'] == current_entity];
        current_pxq_budget_input_data_df = pxq_budget_input_data_df.loc[pxq_budget_input_data_df['entity'] == current_entity];

        current_service_hours = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'SH')]['value']));
        current_reserved_hours = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'RS')]['value']));

        current_available_hours = current_service_hours + current_reserved_hours;


        current_epdh = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'EPDH')]['value']));
        current_eudh = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'EUDH')]['value']));
        current_ph = sum(list(current_pxq_data_df.loc[(current_pxq_data_df['data_source'] == 'A+F') & (current_pxq_data_df['input_title'] == 'PH')]['value']));
        current_eaf = (current_available_hours - current_epdh - current_eudh) / current_ph;

        eaf_list.append([current_entity, current_service_hours, current_reserved_hours, current_available_hours, current_epdh, current_eudh, current_ph, current_eaf])

    if company in NON_GAS_PLANTS_DICT:
        temp_eaf_list = [];

        non_gas_plant_list = NON_GAS_PLANTS_DICT[company];
        gas_plants_list = list(set(entity_list) - set(non_gas_plant_list));
        current_entity = 'Gas Plants';
        current_service_hours = sum([item[1] for item in eaf_list if item[0] not in non_gas_plant_list]);
        current_reserved_hours = sum([item[2] for item in eaf_list if item[0] not in non_gas_plant_list]);
        current_available_hours = sum([item[3] for item in eaf_list if item[0] not in non_gas_plant_list]);
        current_epdh = sum([item[4] for item in eaf_list if item[0] not in non_gas_plant_list]);
        current_eudh = sum([item[5] for item in eaf_list if item[0] not in non_gas_plant_list]);
        current_ph = sum([item[6] for item in eaf_list if item[0] not in non_gas_plant_list]);

        current_eaf = (current_available_hours - current_epdh - current_eudh) / current_ph;
        temp_eaf_list.append([current_entity, current_service_hours, current_reserved_hours, current_available_hours, current_epdh, current_eudh, current_ph, current_eaf])

        current_entity = non_gas_plant_list[0];
        current_service_hours = sum([item[1] for item in eaf_list if item[0] in non_gas_plant_list]);
        current_reserved_hours = sum([item[2] for item in eaf_list if item[0] in non_gas_plant_list]);
        current_available_hours = sum([item[3] for item in eaf_list if item[0] in non_gas_plant_list]);
        current_epdh = sum([item[4] for item in eaf_list if item[0] in non_gas_plant_list]);
        current_eudh = sum([item[5] for item in eaf_list if item[0] in non_gas_plant_list]);
        current_ph = sum([item[6] for item in eaf_list if item[0] in non_gas_plant_list]);

        current_eaf = (current_available_hours - current_epdh - current_eudh) / current_ph;
        temp_eaf_list.append([current_entity, current_service_hours, current_reserved_hours, current_available_hours, current_epdh, current_eudh, current_ph, current_eaf])

        current_entity = company;
        current_service_hours = sum([item[1] for item in eaf_list]);
        current_reserved_hours = sum([item[2] for item in eaf_list]);
        current_available_hours = sum([item[3] for item in eaf_list]);
        current_epdh = sum([item[4] for item in eaf_list]);
        current_eudh = sum([item[5] for item in eaf_list]);
        current_ph = sum([item[6] for item in eaf_list]);

        current_eaf = (current_available_hours - current_epdh - current_eudh) / current_ph;
        temp_eaf_list.append([current_entity, current_service_hours, current_reserved_hours, current_available_hours, current_epdh, current_eudh, current_ph, current_eaf])

        eaf_list = eaf_list + temp_eaf_list;

    pxq_ytd_ready_list.append(eaf_list);


    return pxq_ytd_ready_list;




def get_pxq_mtd_ready(company,month_date_obj, pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df):

    pxq_mtd_ready_list = [];

    print (month_date_obj);

    print (len(pxq_input_data_df), len(pxq_budget_input_data_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df));

    pxq_financials_actuals_df = pxq_financials_actuals_df.loc[(pxq_financials_actuals_df['account'].isin(ACTUALS_FINANCIALS_FSLI_LIST)) & (pxq_financials_actuals_df['period'] == month_date_obj)];
    pxq_financials_budget_df = pxq_financials_budget_df.loc[(pxq_financials_budget_df['account'].isin(BUDGET_FINANCIALS_FSLI_LIST)) & (pxq_financials_budget_df['period'] == month_date_obj)];


    # print (set(list(pxq_financials_actuals_df['account'])));
    # print (set(list(pxq_financials_budget_df['account'])));

    for i in range(0, len(pxq_financials_actuals_df)):
        current_entity = pxq_financials_actuals_df.iloc[i]['entity'];
        current_account = pxq_financials_actuals_df.iloc[i]['account'];
        current_value = pxq_financials_actuals_df.iloc[i]['value'];
        pxq_mtd_ready_list.append(['ACTUALS',current_entity, current_account, str(month_date_obj).split(" ")[0], current_value]);

    for i in range(0, len(pxq_financials_budget_df)):
        current_entity = pxq_financials_budget_df.iloc[i]['entity'];
        current_account = pxq_financials_budget_df.iloc[i]['account'];
        current_value = pxq_financials_budget_df.iloc[i]['value'];
        pxq_mtd_ready_list.append(['BUDGET',current_entity, current_account, str(month_date_obj).split(" ")[0], current_value]);

    pxq_budget_account_name_list = ['On-Peak Generation','Off-Peak Generation','Total Generation', 'Realized On-Peak Power Price','Realized Off-Peak Power Price','Fossil Fuel Consumed'];
    pxq_mtd_budget_df = pxq_budget_input_data_df.loc[(pxq_budget_input_data_df['period'] == month_date_obj) & (pxq_budget_input_data_df['account_name'].isin(pxq_budget_account_name_list))];

    for i in range(0, len(pxq_mtd_budget_df)):
        current_entity = pxq_mtd_budget_df.iloc[i]['entity'];
        current_account = pxq_mtd_budget_df.iloc[i]['account_name'];
        current_value = pxq_mtd_budget_df.iloc[i]['value'];
        pxq_mtd_ready_list.append(['BUDGET',current_entity, current_account, str(month_date_obj).split(" ")[0], current_value]);


    pxq_mtd_title_list = ['Period Hours','Budget Capacity','Total Generation', 'SH', 'RS', 'EPDH','EUDH','PH','Equivalent Availablity Factor (EAF) %','Fuel Burn'];
    pxq_input_data_df = pxq_input_data_df.loc[(pxq_input_data_df['input_title'].isin(pxq_mtd_title_list)) & (pxq_input_data_df['period'] == month_date_obj)];

    for i in range(0, len(pxq_input_data_df)):
        current_entity = pxq_input_data_df.iloc[i]['entity'];
        current_account = pxq_input_data_df.iloc[i]['input_title'];
        current_value = pxq_input_data_df.iloc[i]['value'];
        pxq_mtd_ready_list.append(['PXQ',current_entity, current_account, str(month_date_obj).split(" ")[0], current_value]);


    print (len(pxq_input_data_df), len(pxq_mtd_budget_df), len(pxq_financials_actuals_df), len(pxq_financials_budget_df));

    # pxq_mtd_ready_list.sort(key=lambda val:(COMPANY_ENTITY_ORDER_DICT[company][val[1]], val[2]));

    return pxq_mtd_ready_list;


def prepare_pxq_data_mtd_ytd(conn_ins, company, amr_scenario, amr_version, budget_scenario, budget_version):
    pxq_input_data_df = db_controller_support.get_pxq_input_data(conn_ins, amr_scenario, company);
    pxq_budget_input_data_df = db_controller_support.get_budget_input_data_for_pxq(conn_ins, budget_scenario, company);
    pxq_financials_actuals_df = db_controller_support.get_financials(conn_ins, company, amr_scenario, amr_version);
    pxq_financials_budget_df = db_controller_support.get_financials(conn_ins, company, budget_scenario, budget_version);
    pxq_dispatch_df = db_controller_support.get_dispatch(conn_ins, company, amr_scenario);
    return pxq_input_data_df, pxq_budget_input_data_df, pxq_financials_actuals_df, pxq_financials_budget_df, pxq_dispatch_df;


def get_pxq_pnl_ready(conn_ins, company, amr_scenario, budget_scenario):
    pxq_input_data_df = db_controller_support.get_pxq_input_data(conn_ins, amr_scenario, company);
    pxq_budget_input_data_df = db_controller_support.get_budget_input_data_for_pxq(conn_ins, budget_scenario, company);
    # print (len(pxq_input_data_df));
    on_off_peak_ratio_list = [];

    current_month = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[0][-1];

    current_month_obj = datetime.datetime.strptime(current_month, '%Y-%m-%d').date();

    print (current_month);

    pxq_pnl_title_list = ['On Peak Generation','Off Peak Generation','On Peak Realized Power Price', 'Off Peak Realized Power Price'];
    pxq_pnl_pi_df = pxq_input_data_df.loc[(pxq_input_data_df['input_title'].isin(pxq_pnl_title_list)) & (pxq_input_data_df['data_source'] == 'PI') & (pxq_input_data_df['period'] == current_month_obj)];

    print (len(pxq_pnl_pi_df));
    # print (len(pxq_budget_input_data_df));

    pxq_budget_account_name_list = ['On-Peak Generation','Off-Peak Generation','Total Generation', 'Realized On-Peak Power Price','Realized Off-Peak Power Price'];

    pxq_pnl_budget_df = pxq_budget_input_data_df.loc[(pxq_budget_input_data_df['period'] == current_month_obj) & (pxq_budget_input_data_df['account_name'].isin(pxq_budget_account_name_list))];
    print (len(pxq_pnl_budget_df));

    pxq_pnl_ready_list = [];

    grouped_pxq_pnl_pi_df = pxq_pnl_pi_df.groupby('entity');

    for current_entity in grouped_pxq_pnl_pi_df.groups:
        current_pxq_pnl_pi_df = grouped_pxq_pnl_pi_df.get_group(current_entity);
        on_peak_gen = current_pxq_pnl_pi_df.loc[current_pxq_pnl_pi_df['input_title'] == 'On Peak Generation'].iloc[0]['value'];
        off_peak_gen = current_pxq_pnl_pi_df.loc[current_pxq_pnl_pi_df['input_title'] == 'Off Peak Generation'].iloc[0]['value'];
        on_peak_rp = current_pxq_pnl_pi_df.loc[current_pxq_pnl_pi_df['input_title'] == 'On Peak Realized Power Price'].iloc[0]['value'];
        off_peak_rp = current_pxq_pnl_pi_df.loc[current_pxq_pnl_pi_df['input_title'] == 'Off Peak Realized Power Price'].iloc[0]['value'];

        pxq_pnl_ready_list.append(['PI Actuals', current_entity, on_peak_gen, off_peak_gen, on_peak_rp, off_peak_rp]);
        on_off_peak_ratio_list.append([current_entity, on_peak_gen/(on_peak_gen+off_peak_gen), off_peak_gen/(on_peak_gen + off_peak_gen)]);

    grouped_pxq_pnl_budget_df = pxq_pnl_budget_df.groupby('entity');

    for current_entity in grouped_pxq_pnl_budget_df.groups:
        current_pxq_pnl_budget_df = grouped_pxq_pnl_budget_df.get_group(current_entity);
        on_peak_gen = current_pxq_pnl_budget_df.loc[current_pxq_pnl_budget_df['account_name'] == 'On-Peak Generation'].iloc[0]['value'];
        off_peak_gen = current_pxq_pnl_budget_df.loc[current_pxq_pnl_budget_df['account_name'] == 'Off-Peak Generation'].iloc[0]['value'];
        on_peak_rp = current_pxq_pnl_budget_df.loc[current_pxq_pnl_budget_df['account_name'] == 'Realized On-Peak Power Price'].iloc[0]['value'];
        off_peak_rp = current_pxq_pnl_budget_df.loc[current_pxq_pnl_budget_df['account_name'] == 'Realized Off-Peak Power Price'].iloc[0]['value'];

        pxq_pnl_ready_list.append(['Budget', current_entity, on_peak_gen, off_peak_gen, on_peak_rp, off_peak_rp]);


    # for item in pxq_pnl_ready_list:
    #     print (item);


    pxq_pnl_ready_list.sort(key=lambda val:(val[0],COMPANY_ENTITY_ORDER_DICT[company][val[1]]));
    on_off_peak_ratio_list.sort(key=lambda val:(COMPANY_ENTITY_ORDER_DICT[company][val[0]]));


    return pxq_pnl_ready_list, on_off_peak_ratio_list;
