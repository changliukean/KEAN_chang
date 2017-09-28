import sys;
import os;
from pathlib import Path;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_estimate;
import db_controller;


NUMBER_OF_UNITS_DICT = {'Gavin':2, 'Lawrenceburg':2, 'Waterford':3, 'Darby':6};

# NUMBER_OF_UNITS_DICT = {'Gavin':2};


def estimate_main(conn_ins, company_name, amr_scenario, estimate_month_dates_list):
    print ("=================   calculating estimates financials results...");

    dispatch_df = db_controller_estimate.get_dispatch_data(conn_ins, amr_scenario, company_name);

    # financials_fixed_fuel_inputs_df = db_controller_estimate.get_financials_data_item(conn_ins, amr_scenario, "Fixed Fuel");
    #
    # financials_hedge_pnl_inputs_df = db_controller_estimate.get_financials_data_item(conn_ins, amr_scenario, "Hedge P&L");

    print (len(dispatch_df));

    dispatch_financials_result_list = get_financials_from_dispatch(dispatch_df, amr_scenario);

    # for item in dispatch_financials_result_list:
    #     print (item);
    # sys.exit();
    db_controller.upload_cal_results_to_financials(conn_ins, dispatch_financials_result_list, company_name, amr_scenario);



def get_financials_from_dispatch(dispatch_df,  scenario):

    result_financials_list = [];

    for item in NUMBER_OF_UNITS_DICT:
        entity_name = item;

        count_units = NUMBER_OF_UNITS_DICT[entity_name];
        print (entity_name, count_units);



        entity_dispatch_df = dispatch_df.loc[dispatch_df['entity']==entity_name];

        company_name = entity_dispatch_df.iloc[0]['company'];

        month_list = list(set(list(dispatch_df['period'])));

        # print (month_list);

        for month in month_list:


            month_dispatch_df = entity_dispatch_df.loc[entity_dispatch_df['period']==month];
            # print (len(month_dispatch_df));
            energy_revenue = month_dispatch_df.loc[month_dispatch_df['fsli']=='On-Peak Generation'].iloc[0]['value'] \
                           * month_dispatch_df.loc[month_dispatch_df['fsli']=='Realized On-Peak Power Price'].iloc[0]['value']\
                           + month_dispatch_df.loc[month_dispatch_df['fsli']=='Off-Peak Generation'].iloc[0]['value'] \
                           * month_dispatch_df.loc[month_dispatch_df['fsli']=='Realized Off-Peak Power Price'].iloc[0]['value'];

            energy_revenue = energy_revenue * 1000;

            # print (month, energy_revenue);

            delivered_fuel_expense = (month_dispatch_df.loc[month_dispatch_df['fsli']=='On-Peak Generation'].iloc[0]['value'] \
                                   + month_dispatch_df.loc[month_dispatch_df['fsli']=='Off-Peak Generation'].iloc[0]['value'])\
                                   * month_dispatch_df.loc[month_dispatch_df['fsli']=='Plant Heat Rate'].iloc[0]['value']\
                                   * month_dispatch_df.loc[month_dispatch_df['fsli']=='Delivered Fuel Cost'].iloc[0]['value'] * 1000.0;

            delivered_fuel_expense = delivered_fuel_expense ;

            # print (month, delivered_fuel_expense);


            net_emission_expense = month_dispatch_df.loc[month_dispatch_df['fsli']=='Net Emissions Expense'].iloc[0]['value'];

            net_emission_expense = net_emission_expense * 1000;

            # print (type(month), month);

            """
                be careful
                here we made some special modifications for Gavin
                this explains why the numbers we generated for Gross Margin of gas plants
                are different from what we see in the dispatch model
            """
            if entity_name == 'Gavin' and str(month) in ['2017-09-30','2017-11-30']:
                net_emission_expense = 167633.9174/2.0;

            vom = month_dispatch_df.loc[month_dispatch_df['fsli']=='Variable O&M Cost'].iloc[0]['value'];
            if entity_name != 'Gavin':
                vom = 0.0;
            vom = vom * 1000;

            # gross_energy_margin = month_dispatch_df.loc[month_dispatch_df['fsli']=='Gross Energy Margin'].iloc[0]['value'];
            # gross_energy_margin = gross_energy_margin * 1000;

            # fixed_fuel_item = financials_fixed_fuel_inputs_df.loc[(financials_fixed_fuel_inputs_df['entity']==entity_name) & (financials_fixed_fuel_inputs_df['period'] == month) ];
            #
            # fixed_fuel_value = fixed_fuel_item.iloc[0]['value'] if len(fixed_fuel_item) > 0 else 0.0;

            # gross_energy_margin = 0.0;

            # hedge_pnl_item = financials_hedge_pnl_inputs_df.loc[(financials_hedge_pnl_inputs_df['entity']==entity_name) & (financials_hedge_pnl_inputs_df['period'] == month) ];
            #
            # hedge_pnl_value = hedge_pnl_item.iloc[0]['value'] if len(hedge_pnl_item) > 0 else 0.0;

            # net_energy_margin = 0.0;


            result_financials_list.append([company_name, entity_name, scenario, "Energy Revenue", month, energy_revenue]);
            result_financials_list.append([company_name, entity_name, scenario, "Delivered Fuel Expense", month, delivered_fuel_expense]);
            result_financials_list.append([company_name, entity_name, scenario, "Net Emissions Expense", month, net_emission_expense]);
            result_financials_list.append([company_name, entity_name, scenario, "Variable O&M Expense", month, vom]);
            result_financials_list.append([company_name, entity_name, scenario, "Gross Energy Margin", month, 0.0]);
            result_financials_list.append([company_name, entity_name, scenario, "Net Energy Margin", month, 0.0]);






    return result_financials_list;
