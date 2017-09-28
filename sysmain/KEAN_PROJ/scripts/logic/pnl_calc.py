import os;
import sys;
import pandas as pd;
import datetime;

"""
    import a module/script from a sibling folder
"""
dir_path = os.path.dirname(os.path.realpath(__file__));
parent_path = os.path.abspath(os.path.join(dir_path, os.pardir));
parent_path = parent_path + '/db_utils/';
sys.path.insert(0,parent_path)
import db_controller;


parent_path = os.path.abspath(os.path.join(dir_path, os.pardir));
parent_path = parent_path + '/general_utils/';
sys.path.insert(0,parent_path)
import date_util;



"""
    method: get_pnl_for_entity_in_dates
    give the company name, go to the database to find out all powerplants/entities under this company
    give the date range, we calculate pnl for each day
    we also calculate a pnl result for 'as of date' or the accumalated value for the date range
    return a list of results that will be loaded to financials table

    inputs/parameters:
    1. conn_ins
       the db connection instance
       we will have to do database access here, so we need to pass the database instance we initiated.
       the reason for passing this as a parameter is we will have multiple calculators to use the connection
       but we dont want to create multiple connection instances which is space-and-time wasting.
    2. start_date
       a string of start date in "yyyy-mm-dd" format
    3. end_date
       a string of end date in "yyyy-mm-dd" format
    4. entity_name=None,
       default to 'None' meaning do calculations for all entities under the company_name
       if specified, we only calculate for the entity


    if we want to calculate a daily pnl for a specific date, we simply pass same date for start_date and end_date

    detailed steps:
    1. prepare data
       we do one time db access to get all the data we need for calculating daily pnl
       too many db access will slow down the program
    2. calculation
       give input data, we do calculations
    3. prepare result list
       return the result list in the format for uploading to 'financials' table

"""


HOST = 'kindledb.cfdmlfy5ocmf.us-west-2.rds.amazonaws.com';
USER = 'Andrew';
PASSWORD = 'Kindle01';
DATABASE = 'poc_test_cl';


def generate_connection_instance(host, user, password, database):
    connection_instance = mysql.connector.connect(host = host,user = user, password = password, database = database)
    return connection_instance;




def get_pnl_for_company_in_dates(conn_ins, company_name, start_date_str, end_date_str, entity_name=None):

    """ get dates list """
    dates_list = date_util.get_dates_list(start_date_str, end_date_str);

    account_name_value_list = [];

    if entity_name == None:

        company_entity_df = db_controller.get_company_entity_info_by_company_name(conn_ins,company_name);
        # print (company_entity_df);


        for i in range(0, len(company_entity_df)):
            entity_name = company_entity_df.iloc[i]['entity_name'];

            entity_info_df,\
            da_awards_df,\
            dart_prices_df,\
            generation_df,\
            operations_costs_df,\
            fuel_cost_track_info_df,\
            fuel_cost_track_info_list = prepare_data_for_daily_pnl(conn_ins, company_name, entity_name ,dates_list);
            account_name_value_list = get_financials_result_list(conn_ins, company_name, entity_name, start_date_str, end_date_str, dates_list,
                                   entity_info_df,\
                                   da_awards_df,\
                                   dart_prices_df,\
                                   generation_df,\
                                   operations_costs_df,\
                                   fuel_cost_track_info_df);

    else:

        entity_info_df,\
        da_awards_df,\
        dart_prices_df,\
        generation_df,\
        operations_costs_df,\
        fuel_cost_track_info_df,\
        fuel_cost_track_info_list,\
        unit_name_list = prepare_data_for_daily_pnl(conn_ins, company_name, entity_name ,dates_list);

        # print (len(entity_info_df));
        # print (len(da_awards_df));
        # print (len(dart_prices_df));
        # print (len(generation_df));
        # print (len(operations_costs_df));
        # print (len(fuel_cost_track_info_df));
        account_name_value_list = get_financials_result_list(conn_ins, company_name, entity_name, start_date_str, end_date_str, dates_list,
                                   entity_info_df,\
                                   da_awards_df,\
                                   dart_prices_df,\
                                   generation_df,\
                                   operations_costs_df,\
                                   fuel_cost_track_info_list,\
                                   unit_name_list);

    return account_name_value_list;



def get_financials_result_list(conn_ins, company_name, entity_name, start_date_str, end_date_str, dates_list,
                               entity_info_df,\
                               da_awards_df,\
                               dart_prices_df,\
                               generation_df,\
                               operations_costs_df,\
                               fuel_cost_track_info_list,\
                               unit_name_list):

    account_name_value_list  = [];

    engrev_gen_onoffpeak_result_list = get_engrev_gen_onoffpeak_daily(conn_ins, generation_df, da_awards_df, dart_prices_df, dates_list)
    sumup_result_revenue = 0.0;
    sumup_result_generation = 0.0;
    sumup_result_on_peak = 0.0;
    sumup_result_off_peak = 0.0;

    for item in engrev_gen_onoffpeak_result_list:
        sumup_result_revenue += item[0];
        sumup_result_on_peak += item[1];
        sumup_result_off_peak += item[2];
        sumup_result_generation += item[3];
        # print (item[0], item[1], item[2], item[3], item[4]);
        account_name_value_list.append([company_name, entity_name, item[4], str(item[4]) + ' Daily PNL Actuals', 'Energy Revenue (DA & RT)', item[4],item[0]]);
        account_name_value_list.append([company_name, entity_name, item[4], str(item[4]) + ' Daily PNL Actuals', 'On-Peak Revenue', item[4],item[1]]);
        account_name_value_list.append([company_name, entity_name, item[4], str(item[4]) + ' Daily PNL Actuals', 'Off-Peak Revenue', item[4],item[2]]);


    print ('===================================================');
    print ('energy revenue:  ',sumup_result_revenue);
    print ('on-peak rev:  ',sumup_result_on_peak);
    print ('off-peak rev:  ',sumup_result_off_peak);
    print ('generation:  ',sumup_result_generation);
    print ('===================================================');

    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Energy Revenue (DA & RT)', end_date_str, sumup_result_revenue]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'On-Peak Revenue', end_date_str, sumup_result_on_peak]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Off-Peak Revenue', end_date_str, sumup_result_off_peak]);

    daily_delivered_fuel_cost_result_list, fuel_expense_result_df = get_delivered_fuel_expense_daily(conn_ins,fuel_cost_track_info_list, dates_list, company_name, entity_name);


    sumup_delivered_fuel_cost = 0.0;
    for item in daily_delivered_fuel_cost_result_list:
        sumup_delivered_fuel_cost += item[3];
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Delivered Fuel Expense', item[0],item[3]]);

    print ('===================================================');
    print ('delivered fuel cost:  ',sumup_delivered_fuel_cost);
    print ('===================================================');
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Delivered Fuel Expense', end_date_str, sumup_delivered_fuel_cost]);

    daily_emissions_expense_result_list = get_emissions_expense_daily(conn_ins, operations_costs_df, dates_list, company_name, entity_name);
    sumup_emissions_expense = 0.0;
    for item in daily_emissions_expense_result_list:
        sumup_emissions_expense += item[3];
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Net Emissions Expense', item[0],item[3]]);

    print ('===================================================');
    print ('net emissions expense:  ',sumup_emissions_expense);
    print ('===================================================');
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Net Emissiosn Expense', end_date_str, sumup_emissions_expense]);


    daily_vom_expense_result_list, vom_expense_result_df = get_vom_expense(conn_ins, operations_costs_df, generation_df, company_name, entity_name, unit_name_list, dates_list);

    sumup_vom_expense = 0.0;
    for item in daily_vom_expense_result_list:
        sumup_vom_expense += item[3];
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Variable O&M Expense', item[0],item[3]]);

    print ('===================================================');
    print ('net variable O&M expense:  ',sumup_vom_expense);
    print ('===================================================');
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Variable O&M Expense', end_date_str, sumup_vom_expense]);

    daily_gross_energy_margin_result_list = get_gross_energy_margin(company_name, entity_name, unit_name_list, dates_list,
                                           engrev_gen_onoffpeak_result_list,
                                           daily_delivered_fuel_cost_result_list,
                                           daily_emissions_expense_result_list,
                                           daily_vom_expense_result_list
                                           );
    sumup_gross_energy_margin = 0.0;
    for item in daily_gross_energy_margin_result_list:
        sumup_gross_energy_margin += item[3];
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Gross Energy Margin', item[0],item[3]]);

    print ('===================================================');
    print ('Gross Energy Margin:  ',sumup_gross_energy_margin);
    print ('===================================================');
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Gross Energy Margin', end_date_str, sumup_gross_energy_margin]);

    sumup_hedge_pnl = 0.0;
    sumup_net_energy_margin = 0.0;
    sumup_capacity_revenue = 0.0;
    sumup_ancillary_revenue = 0.0;
    sumup_total_other_income = 0.0;
    daily_hedge_pnl_result_list = get_hedgepnl_caprev_ancrev_netengmarg_otherincome(conn_ins, operations_costs_df, company_name, entity_name, dates_list, daily_gross_energy_margin_result_list);
    for item in daily_hedge_pnl_result_list:
        sumup_hedge_pnl += item[3];
        sumup_net_energy_margin += item[4];
        sumup_capacity_revenue += item[5];
        sumup_ancillary_revenue += item[6];
        sumup_total_other_income += item[7];

        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Hedge P&L', item[0],item[3]]);
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Net Energy Margin w/ Hedge P&L', item[0],item[4]]);
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Capacity Revenue', item[0],item[5]]);
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Ancillary Revenue', item[0],item[6]]);
        account_name_value_list.append([company_name, entity_name, item[0], str(item[0]) + ' Daily PNL Actuals', 'Total Other Income', item[0],item[7]]);


    print ('===================================================');
    print ('Hedge P&L:  ',sumup_hedge_pnl);
    print ('Net Energy Margin w/ Hedge P&L', sumup_net_energy_margin);
    print ('Capacity Revenue:  ',sumup_capacity_revenue);
    print ('Ancillary Revenue:  ',sumup_ancillary_revenue);
    print ('Total Other Income: ', sumup_total_other_income);
    print ('===================================================');
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Hedge P&L', end_date_str, sumup_hedge_pnl]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Net Energy Margin w/ Hedge P&L', end_date_str, sumup_net_energy_margin]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Capacity Revenue', end_date_str, sumup_capacity_revenue]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Ancillary Revenue', end_date_str, sumup_ancillary_revenue]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Total Other Income', end_date_str, sumup_total_other_income]);


    daily_mtd_gross_margin_result_list = get_mtd_gross_margin(conn_ins, operations_costs_df ,company_name, entity_name, dates_list, daily_hedge_pnl_result_list);

    sumup_fix_transport_cost = 0.0;
    sumup_mtd_gross_margin = 0.0;

    for item in daily_mtd_gross_margin_result_list:
        sumup_fix_transport_cost += item[3];
        sumup_mtd_gross_margin += item[4];
        account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Daily PNL Actuals", 'Fixed Fuel Transport & Storage Costs', end_date_str, item[3]]);
        account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Daily PNL Actuals", 'MTD Gross Margin', end_date_str, item[4]]);


    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'Fixed Fuel Transport & Storage Costs', end_date_str, sumup_fix_transport_cost]);
    account_name_value_list.append([company_name, entity_name, end_date_str, end_date_str + " Accu PNL Actuals", 'MTD Gross Margin', end_date_str, sumup_mtd_gross_margin]);


    print ('===================================================');
    print ('Fixed Fuel Transport & Storage Costs:  ',sumup_fix_transport_cost);
    print ('MTD Gross Margin', sumup_mtd_gross_margin);
    print ('===================================================');

    return account_name_value_list;


def prepare_data_for_daily_pnl(conn_ins, company_name, entity_name, dates_list):
    dates_condition_sql_str = date_util.get_sql_where_clause_for_dates(dates_list);

    """get entity_info_df """
    entity_info_df = db_controller.get_entity_info(conn_ins, entity_name);

    unit_name_list = [entity_info_df.iloc[i]['unit'] for i in range(0, len(entity_info_df))];

    unit_name = unit_name_list[0];

    """ get pnode id"""
    pnode_id_table_name = 'power_plants';
    pnode_id_select_list = ['pnode_id'];
    pnode_id_where_clause = "WHERE power_plant_name = \'" + entity_name + "\' and unit = \'" + unit_name + "\' LIMIT 1";
    pnode_id_df = db_controller.get_query_df_by_where_clause(conn_ins, pnode_id_table_name, pnode_id_select_list, pnode_id_where_clause);
    # print (pnode_id_df);
    pnode_id = pnode_id_df.iloc[0]['pnode_id'];
    # print ("----------------------pnoid-------------------------");
    # print (pnode_id);


    """ get da awards """
    da_awards_where_clause = "WHERE delivery_date " + dates_condition_sql_str + " AND power_plant = \'" + entity_name + "\' ;";
    da_awards_table_name = "da_awards";
    da_awards_select_list = ["*"];
    da_awards_df = db_controller.get_query_df_by_where_clause(conn_ins, da_awards_table_name, da_awards_select_list, da_awards_where_clause);
    # print ("----------------------awadf-------------------------");
    # print (da_awards_df);

    """ get da and rt prices """
    dart_prices_table_name = "lmp";
    dart_prices_select_list = ["*"];
    dart_prices_where_clause = "WHERE valuation_date " + dates_condition_sql_str + " AND pnode_id = \'" + pnode_id + "\'";
    dart_prices_df = db_controller.get_query_df_by_where_clause(conn_ins, dart_prices_table_name, dart_prices_select_list , dart_prices_where_clause);
    # print ("--------------------pridf---------------------------");
    # print (dart_prices_df);


    """ get generation  """

    generation_table_name = 'generation';
    generation_select_list = ['*'];
    generation_where_clause = " WHERE generation_date " + dates_condition_sql_str + " AND  power_plant = \'" + entity_name + "\'";
    generation_df = db_controller.get_query_df_by_where_clause(conn_ins, generation_table_name, generation_select_list, generation_where_clause);


    """ get operating_costs """
    operating_costs_table_name = 'operating_costs';
    operating_costs_select_list = ['*'];
    operating_costs_where_clause = " WHERE power_plant_name = \'" + entity_name + "\' ;";
    operations_costs_df = db_controller.get_query_df_by_where_clause(conn_ins, operating_costs_table_name, operating_costs_select_list, operating_costs_where_clause);



    """ get fuel cost track info list """

    """ this part is a little bit complex cuz Gavin is a special case """

    fuel_expense_result_df = pd.DataFrame(columns = ('date', 'fuel_price_data_date', 'hour_ending', 'fuel_price_period', 'fuel_burn', 'fuel_price', 'fuel_cost', 'variable_transport', 'delivered_fuel_cost'));


    """ get variable transport price """
    var_transport_price = float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'var_transport_price'].iloc[0]['amount']);


    fuel_cost_track_info_list = [];
    """ loop through each unit """

    for unit_name in unit_name_list:
        """ get fuel instrument id"""

        fuel_instrument_id = str(entity_info_df.loc[(entity_info_df["power_plant_name"] == entity_name) & (entity_info_df["unit"] == unit_name)].iloc[0]["fuel_instrument_id"]);



        """ get data of fuel burn for each unit """

        fuel_burn_track_info_df = pd.DataFrame(columns = ('date','hour_ending','fuel_burn'));
        fuel_burn_track_info_list = [];
        track_index = 0;

        if entity_name == "Gavin":

            heat_rate_value = float(entity_info_df.loc[(entity_info_df["power_plant_name"] == entity_name) & (entity_info_df["unit"] == unit_name)].iloc[0]["heat_rate"]);

            generation_unit_df = generation_df.loc[generation_df['unit'] == unit_name];

            for i in range(0, len(generation_unit_df)):
                fuel_burn_for_hour_ending = generation_unit_df.iloc[i]['generation'] * heat_rate_value;
                hour_ending = generation_unit_df.iloc[i]['hour_ending'];
                date_str = generation_unit_df.iloc[i]['generation_date'];
                fuel_burn_track_info_df.loc[track_index] = [date_str, hour_ending, fuel_burn_for_hour_ending];
                track_index += 1;

        else:
            fuel_burn_table_name = "fuel_burn";
            fuel_burn_select_list = ['*'];
            fuel_burn_where_clause = " WHERE power_plant = \'" + entity_name + "\' AND unit =\'" + unit_name + "\' ;";
            fuel_burn_df = db_controller.get_query_df_by_where_clause(conn_ins, fuel_burn_table_name, fuel_burn_select_list, fuel_burn_where_clause);
            for i in range(0, len(fuel_burn_df)):
                fuel_burn_for_hour_ending = fuel_burn_df.iloc[i]['burn'] ;
                hour_ending = fuel_burn_df.iloc[i]['hour_ending'];
                date_str = fuel_burn_df.iloc[i]['burn_date'];
                fuel_burn_track_info_df.loc[track_index] = [date_str, hour_ending, fuel_burn_for_hour_ending];
                track_index += 1;

        # print ("======================");
        # print (len(fuel_burn_track_info_df));
        # print ("======================");

        # """ SELECT price FROM prices WHERE instrument_id = %s AND valuation_date = %s AND period = %s """

        """ get fuel price for each unit based on the instrument_id  """

        day_ahead = date_util.get_date_ahead(dates_list[0]);
        day_after = date_util.get_date_after(dates_list[-1]);

        dates_list_for_fuel_prices = [day_ahead] + dates_list + [day_after];
        fuel_prices_dates_condition_sql_str = date_util.get_sql_where_clause_for_dates(dates_list_for_fuel_prices);


        fuel_prices_table_name = 'prices';
        fuel_prices_select_list = ['*'];
        fuel_prices_where_clause = " WHERE instrument_id = \'" + fuel_instrument_id + "\' AND data_date " + fuel_prices_dates_condition_sql_str + " ;";
        fuel_prices_df = db_controller.get_query_df_by_where_clause(conn_ins, fuel_prices_table_name,fuel_prices_select_list, fuel_prices_where_clause);

        # print ("======================");
        # print (fuel_prices_df);
        # print ("======================");


        """ calculating the fuel cost """
        fuel_cost_track_info_df = pd.DataFrame(columns = ('date','hour_ending', 'fuel_price_data_date', 'fuel_price_period', 'fuel_burn', 'fuel_price', 'fuel_cost', 'variable_transport', 'delivered_fuel_cost'));

        track_index = 0;
        for i in range(0, len(fuel_burn_track_info_df)):
            hour_ending = fuel_burn_track_info_df.iloc[i]['hour_ending'];
            fuel_burn_date = fuel_burn_track_info_df.iloc[i]['date'];
            fuel_price_data_date = fuel_burn_date;
            if hour_ending < '1000':
                fuel_price_data_date = date_util.get_date_ahead(fuel_burn_date);

            fuel_price_period = fuel_price_data_date;
            fuel_burn_value = fuel_burn_track_info_df.iloc[i]['fuel_burn'];


            fuel_price_value = fuel_prices_df.loc[(fuel_prices_df['data_date'] == fuel_price_data_date) & (fuel_prices_df['period']==fuel_price_period)]['price'];

            fuel_cost = fuel_burn_value * fuel_price_value;

            var_transport_value = fuel_burn_value * var_transport_price;

            delivered_fuel_cost_value = fuel_cost + var_transport_value;

            fuel_cost_track_info_df.loc[track_index] = [fuel_burn_date,
                                                          hour_ending,
                                                          fuel_price_data_date,
                                                          fuel_price_period,
                                                          fuel_burn_value,
                                                          fuel_price_value,
                                                          fuel_cost,
                                                          var_transport_value,
                                                          delivered_fuel_cost_value
                                                         ];
            fuel_cost_track_info_list.append([unit_name, fuel_burn_date,
                                              hour_ending,
                                              fuel_price_data_date,
                                              fuel_price_period,
                                              fuel_burn_value,
                                              fuel_price_value,
                                              fuel_cost,
                                              var_transport_value,
                                              delivered_fuel_cost_value
                                             ]);

            track_index += 1;



    # print (len(fuel_cost_track_info_df));
    # print (len(fuel_cost_track_info_list));

    # for i in range(0, len(fuel_cost_track_info_df)):
    #     print (fuel_cost_track_info_df.iloc[i]);
    #
    # for item in fuel_cost_track_info_list:
    #     print (item);



    return entity_info_df, da_awards_df, dart_prices_df, generation_df, operations_costs_df, fuel_cost_track_info_df, fuel_cost_track_info_list, unit_name_list;

def get_peak_offpeak_coef(iso_options, date_str):

    if date_util.is_weekend_or_holiday(date_str):
        on_peak = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
        off_peak = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1];
        return on_peak, off_peak;

    if iso_options == "PJM":
        on_peak = [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0];
        off_peak = [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1];
        return on_peak,off_peak;

    if iso_options == 'ERCOT':
        on_peak = [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0];
        off_peak = [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1];
        return on_peak,off_peak;

def get_engrev_gen_onoffpeak_daily(conn_ins, generation_df, da_awards_df, dart_prices_df, dates_list):


    energy_revenue_result_list = [];

    hour_ending_list = [ str(i)+"00" if len(str(i)) > 1 else "0" + str(i) + "00"  for i in range(1,25)];

    for date_str in dates_list:
        on_peak, off_peak = get_peak_offpeak_coef("PJM", date_str);


        da_awards_df_daily = da_awards_df.loc[da_awards_df['delivery_date'] == date_str];
        dart_prices_df_daily = dart_prices_df.loc[dart_prices_df['valuation_date'] == date_str];
        generation_df_daily = generation_df.loc[generation_df['generation_date'] == date_str];

        """ calc da_revenue """;
        da_revenue = [];
        da_revenue_track_info = pd.DataFrame(columns = ('hour ending','da award', 'da price', 'award * price'));
        track_index = 0;
        for hour_ending_item in hour_ending_list:
            try:
                da_award_hour = float(da_awards_df_daily.loc[da_awards_df_daily['hour_ending'] == hour_ending_item]['award']);
                da_price_hour = float(dart_prices_df_daily.loc[(dart_prices_df_daily['hour_ending'] == hour_ending_item) & (dart_prices_df_daily['dart'] == 'Day Ahead') ]['total_lmp']);
                da_revenue_track_info.loc[track_index] = [hour_ending_item,
                                                          da_award_hour,
                                                          da_price_hour,
                                                          da_award_hour * da_price_hour
                                                         ];
                da_revenue.append(da_award_hour * da_price_hour);
                track_index += 1;
            except:
                print ("For hour ending:  "+hour_ending_item, " we miss data inputs for da_revenue." );


        # print ("-----------------------------------------------");
        # print (da_revenue_track_info);




        """ calc rt_revenue """
        rt_revenue = [];
        rt_revenue_track_info = pd.DataFrame(columns = ('hour ending','generation', 'da award', 'generation - da award','rt price' ,'(gen - da award) * rt price'));
        track_index = 0;
        for hour_ending_item in hour_ending_list:
            # print (hour_ending_item);
            try:
                temp_gen_df = generation_df_daily.loc[generation_df_daily['hour_ending'] == hour_ending_item];
                temp_gen = sum([temp_gen_df['generation'].iloc[i] for i in range(0, len(temp_gen_df['generation']))]);
                temp_da_award = float(da_awards_df_daily.loc[da_awards_df['hour_ending'] == hour_ending_item]['award']);
                rt_imbalance_hour = temp_gen - temp_da_award;
                rt_price_hour = float(dart_prices_df_daily.loc[(dart_prices_df_daily['hour_ending'] == hour_ending_item) & (dart_prices_df_daily['dart'] == 'Real Time')]['total_lmp']);
                temp_rt_revenue = rt_imbalance_hour * rt_price_hour;
                rt_revenue_track_info.loc[track_index] = [hour_ending_item,
                                                          temp_gen,
                                                          temp_da_award,
                                                          rt_imbalance_hour,
                                                          rt_price_hour,
                                                          temp_rt_revenue
                                                         ];
                rt_revenue.append(temp_rt_revenue);
                track_index += 1;
            except:
                print ("For hour ending:  "+hour_ending_item, " we miss data inputs for rt_revenue.");


        # print ("-----------------------------------------------");
        # print (rt_revenue_track_info);


        energy_revenue = sum([da_revenue[i] + rt_revenue[i] for i in range(0,24)]);
        on_peak_revenue = sum([(da_revenue[i] + rt_revenue[i]) * on_peak[i] for i in range(0,24)]);
        off_peak_revenue = sum([(da_revenue[i] + rt_revenue[i]) * off_peak[i] for i in range(0,24)]);




        # print (energy_revenue);
        # print ('=========================');
        # print ("da_revenue:   ", da_revenue);
        # print ('=========================');
        # print ("rt_revenue:   ", rt_revenue)
        # print ('=========================');
        # print ("Generation:   ", sum([rt_revenue_track_info['generation'].iloc[i] for i in range(0, len(rt_revenue_track_info['generation']))]));
        # print ('==============================');
        # print ("Energy Revenue:  ", sum(energy_revenue));
        # print ('==============================');
        generation_value = sum([rt_revenue_track_info['generation'].iloc[i] for i in range(0, len(rt_revenue_track_info['generation']))]);

        energy_revenue_result_list.append([energy_revenue, on_peak_revenue, off_peak_revenue, generation_value, date_str,  da_revenue_track_info, rt_revenue_track_info, generation_df]  )


    return energy_revenue_result_list;

def get_delivered_fuel_expense_daily(conn_ins,fuel_cost_track_info_list, dates_list, company_name, entity_name):

    """ sumup all units for hour_ending fuel cost """
    fuel_expense_result_df = pd.DataFrame(columns = ('date', 'fuel_price_data_date', 'hour_ending', 'fuel_price_period', 'fuel_burn', 'fuel_price', 'fuel_cost', 'variable_transport', 'delivered_fuel_cost'));

    track_index = 0;
    hour_ending_list = [ str(i)+"00" if len(str(i)) > 1 else "0" + str(i) + "00"  for i in range(1,25)];



    for date_item in dates_list:
        info_list = [info_item for info_item in fuel_cost_track_info_list if info_item[1] == date_item];
        for hour_ending in hour_ending_list:
            temp_info_list = [info_item for info_item in info_list if info_item[2]==hour_ending];
            # print (len(temp_info_list));
            # print (temp_info_list[0]);
            current_fuel_cost_cell = [temp_info_list[0][1]];
            current_fuel_cost_cell.append(temp_info_list[0][1]);
            current_fuel_cost_cell.append(hour_ending);
            current_fuel_cost_cell.append(temp_info_list[0][3]);
            fuel_burn_value = sum(list(zip(*temp_info_list))[5]);
            fuel_price_value = temp_info_list[0][6];
            fuel_cost = sum(list(zip(*temp_info_list))[7]);
            var_transport = sum(list(zip(*temp_info_list))[8]);
            delivered_fuel_cost = sum(list(zip(*temp_info_list))[9]);
            current_fuel_cost_cell.append(fuel_burn_value);
            current_fuel_cost_cell.append(fuel_price_value);
            current_fuel_cost_cell.append(fuel_cost);
            current_fuel_cost_cell.append(var_transport);
            current_fuel_cost_cell.append(delivered_fuel_cost);
            fuel_expense_result_df.loc[track_index] = current_fuel_cost_cell;
            track_index += 1;


    """ sumup all hour_ending fuel_cost for each day """


    daily_delivered_fuel_cost_result_list= [];
    for date_item in dates_list:
        daily_fuel_cost_df = fuel_expense_result_df.loc[fuel_expense_result_df['date']==date_item];

        # print ("=================================");
        # print (daily_fuel_cost_df);
        # print ("=================================");

        delivered_fuel_cost_daily = sum([ float(daily_fuel_cost_df.iloc[i]['delivered_fuel_cost']) for i in range(0, len(daily_fuel_cost_df))])


        """
            be careful!
            here we changed the sign of the expense value
            from + to -
        """
        daily_delivered_fuel_cost_result_list.append([date_item, company_name, entity_name, -delivered_fuel_cost_daily]);


    return daily_delivered_fuel_cost_result_list, fuel_expense_result_df;

def get_emissions_expense_daily(conn_ins, operations_costs_df, dates_list, company_name, entity_name):

    net_emissions_expense = float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'emissions_cost'].iloc[0]['amount']);
    emissions_expense_result_list = [];
    for date_item in dates_list:
        """
            be careful!
            here we changed the sign of the expense value
            from + to -
        """
        emissions_expense_result_list.append([date_item, company_name, entity_name, -net_emissions_expense]);


    return emissions_expense_result_list;

def get_vom_expense(conn_ins, operations_costs_df, generation_df ,company_name, entity_name, unit_name_list, dates_list):


    vom_price = float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'vom_price'].iloc[0]['amount']);


    vom_expense_result_df = pd.DataFrame(columns = ('unit', 'date','hour_ending', 'generation', 'vom_price', 'vom_expense'));
    track_index = 0;
    for unit_name in unit_name_list:
        generation_unit_df = generation_df.loc[generation_df['unit'] == unit_name];
        for i in range(0, len(generation_unit_df)):
            date_info = generation_unit_df.iloc[i]['generation_date'];
            hour_ending_info = generation_unit_df.iloc[i]['hour_ending'];
            generation_value = generation_unit_df.iloc[i]['generation'];
            vom_expense = vom_price * generation_value;
            vom_expense_result_df.loc[track_index] = [unit_name,
                                                      date_info,
                                                      hour_ending_info,
                                                      generation_value,
                                                      vom_price,
                                                      vom_expense
                                                     ];
            track_index += 1;


    vom_expense_daily_result_list = [];

    for date_item in dates_list:
        daily_vom_df = vom_expense_result_df.loc[vom_expense_result_df['date']==date_item];
        vom_expense_daily = sum([ float(daily_vom_df.iloc[i]['vom_expense']) for i in range(0, len(daily_vom_df))]);


        """
            be careful!
            here we changed the sign of the expense value
            from + to -
        """
        vom_expense_daily_result_list.append([date_item, company_name, entity_name, -vom_expense_daily]);

    return vom_expense_daily_result_list, vom_expense_result_df;

def get_gross_energy_margin(company_name, entity_name, unit_name_list, dates_list ,energy_revenue_result_list, delivered_fuel_cost_result_list, emissions_expense_result_list, vom_expense_result_list):

    daily_gross_energy_margin_result_list = [];
    for date_item in dates_list:
        energy_revenue_value = [item[0] for item in energy_revenue_result_list if item[4]==date_item][0];
        delivered_fuel_expense_value = [item[3] for item in delivered_fuel_cost_result_list if item[0] == date_item][0];
        emission_expense_value = [item[3] for item in emissions_expense_result_list if item[0]==date_item][0];
        vom_expense_value = [item[3] for item in vom_expense_result_list if item[0]==date_item][0];

        gross_energy_margin_value = energy_revenue_value + delivered_fuel_expense_value + emission_expense_value + vom_expense_value;

        daily_gross_energy_margin_result_list.append([date_item, company_name, entity_name, gross_energy_margin_value]);

    return daily_gross_energy_margin_result_list;

def get_hedgepnl_caprev_ancrev_netengmarg_otherincome(conn_ins, operations_costs_df , company_name, entity_name, dates_list, daily_gross_energy_margin_result_list):
    """ right now the hedge pnl is hardcoded to be 0.0 """
    hedge_pnl_value = 0.0;

    capacity_revenue = float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'capacity_rev'].iloc[0]['amount']);
    ancillary_revenue = float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'ancillary_rev'].iloc[0]['amount']);
    total_other_income = hedge_pnl_value + capacity_revenue + ancillary_revenue;

    hpnl_capr_ancr_result_list = [];
    for date_item in dates_list:
        net_energy_margin_with_hpnl = [gross_energy_margin_item[3] for gross_energy_margin_item in  daily_gross_energy_margin_result_list if gross_energy_margin_item[0] == date_item][0] + hedge_pnl_value;
        hpnl_capr_ancr_result_list.append([date_item, company_name, entity_name, hedge_pnl_value, net_energy_margin_with_hpnl ,capacity_revenue, ancillary_revenue, total_other_income]);

    return hpnl_capr_ancr_result_list;

def get_mtd_gross_margin(conn_ins, operations_costs_df, company_name, entity_name, dates_list, hpnl_capr_ancr_result_list):

    fix_transport_price= float(operations_costs_df.loc[operations_costs_df['rev_exp'] == 'fix_transport_price'].iloc[0]['amount']);

    daily_mtd_gross_margin_result_list = [];
    for date_item in dates_list:
        total_other_income_info = [total_other_income_item for total_other_income_item in hpnl_capr_ancr_result_list if total_other_income_item[0] == date_item][0];
        mtd_gross_margin = total_other_income_info[4] + total_other_income_info[7] - fix_transport_price;
        daily_mtd_gross_margin_result_list.append([date_item, company_name, entity_name, fix_transport_price, mtd_gross_margin]);

    return daily_mtd_gross_margin_result_list;
