from pathlib import Path;
import sys;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_budget;
import db_controller;


ACCOUNT_FSLI_MAPPING = {  "ENG":"Energy Revenue","COMFUEL":"Delivered Fuel Expense",\
                          "EMSNEXP":"Net Emissions Expense",\
                          "VARONM":"Variable O&M Expense","FXDFUELTRANS":"Fixed Fuel",\
                          "CAPPAY":"Capacity Revenue","ASR":"Ancillary Services Revenue",\
                          "OTHREVN":"Misc Income","FXDLABEXP":"Labor Expenses",\
                          "MANTPARTS":"Maintenance",\
                          "OPERATIONS":"Operations","ENVSAFTY":"Removal Costs",\
                          "FUELHAND":"Fuel Handling","PRPTYTAX":"Property Tax",\
                          "INSURANCE":"Insurance",\
                          "MANTTOTAL":"Maintenance Capex","ENVTOTAL":"Environmental Capex",\
                          "LTSATOTAL":"LTSA Capex","GROWTHTOTAL":"Growth Capex",
                          "CAMSOMA":"CAMS (OMA fees)","TRANSCOST":"Transition Costs","KINDLEAMA":"Kindle Energy (AMA fees)",
                          "HEDGEPL":"Hedge P&L","ARCTOSAMA":"Arctos","NEXTEMA":"Nextera (EMA fees)"};

FORECAST_BUDGET_FSLI_ITEM_LIST = ['Delivered Fuel Expense','Net Emissions Expense','Variable O&M Expense','Fixed Fuel', 'Labor Expenses',
                                  'Maintenance','Operations','Removal Costs','Fuel Handling','Property Tax','Insurance', 'General & Administrative', 'Maintenance Capex','Environmental Capex','LTSA Capex','Growth Capex'];




def get_budget_financials(conn_ins, budget_df, date_range_list, company_name, scenario, amr_scenario):
    print ("=================   calculating budget financials results...");
    print ("for period, ", date_range_list);
    budget_financials_result_list = [];
    grouped_budget_df = budget_df.groupby(['entity']);

    month_str = str(date_utils.get_month_number(scenario.split(" ")[1])) if len(str(date_utils.get_month_number(scenario.split(" ")[1]))) > 1 else '0'+str(date_utils.get_month_number(scenario.split(" ")[1]));

    data_date = scenario.split(" ")[0] + "-" + month_str + '-01';
    # print (data_date);
    for item in grouped_budget_df.groups:
        for period in date_range_list:

            period_date = date_utils.get_date_from_str(period);
            entity_budget_df = grouped_budget_df.get_group(item);
            entity_budget_df = entity_budget_df.loc[entity_budget_df['period']==period_date];

            entity_name = item;

            plant_id = db_controller_budget.get_entity_plant_id(conn_ins, item);
            tb_mapping_df = db_controller_budget.get_tb_mapping(conn_ins, plant_id, data_date);


            energy_margin = 0.0;
            total_other_income = 0.0;
            gross_margin = 0.0;
            hedgepnl = 0.0;
            net_energy_margin = 0.0;
            fixed_non_labor = 0.0;
            total_fixed_costs = 0.0;
            ebitda = 0.0;
            total_capex = 0.0;
            cf_debt = 0.0;
            ebitda_less_total_capex = 0.0;


            general_and_admin = 0.0;

            for fsli in tb_mapping_df.groups:
                account_list = list(tb_mapping_df.get_group(fsli)['account']);

                current_budget_df = entity_budget_df.loc[entity_budget_df['account'].isin(account_list)];

                fsli_value = sum(list(current_budget_df['value']));

                financials_account = ACCOUNT_FSLI_MAPPING[fsli];
                entity_name = entity_name.strip();

                if financials_account in FORECAST_BUDGET_FSLI_ITEM_LIST:
                    fsli_value = - fsli_value;




                budget_financials_result_list.append([company_name, entity_name, amr_scenario, financials_account, period, fsli_value]);

                if financials_account in ["CAMS (OMA fees)","Transition Costs","Kindle Energy (AMA fees)",\
                          "Arctos","Nextera (EMA fees)"]:
                    general_and_admin -= fsli_value;


            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Gross Energy Margin" , period_date, energy_margin])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Total Other Income", period, total_other_income])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Gross Margin", period, gross_margin])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Net Energy Margin", period, net_energy_margin])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Fixed Non-Labor Expense", period, fixed_non_labor])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Total Fixed Costs", period, total_fixed_costs])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "EBITDA", period, ebitda])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "Total Capex", period, total_capex])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "EBITDA less Capex", period, ebitda_less_total_capex])
            budget_financials_result_list.append([company_name, entity_name, amr_scenario, "General & Administrative", period, general_and_admin])
    return budget_financials_result_list;



"""
    this method is only moving numbers from budget scenario to the amr scenario
"""
def budget_main_forecast(conn_ins, company_name, amr_scenario, budget_scenario, forecast_year_list):
    forecast_start_date = str(forecast_year_list[0]) + "-01-01";
    db_controller_budget.update_forecast_budget_value(conn_ins, company_name, amr_scenario, budget_scenario, forecast_start_date);


def budget_main(conn_ins, company_name, amr_scenario, budget_scenario, year, start_month=1, end_month = 12):

    period_range_list = date_utils.get_month_dates_list(year, start_month, end_month);
    budget_df = db_controller_budget.get_budget_data(conn_ins, company_name, budget_scenario, period_range_list);

    budget_financials_result_list = get_budget_financials(conn_ins,budget_df, period_range_list, company_name, budget_scenario, budget_scenario);

    db_controller.upload_cal_results_to_financials(conn_ins, budget_financials_result_list, company_name, budget_scenario, version='vf');
    db_controller.update_financials_calcs(conn_ins, budget_scenario, company_name, period_range_list, 'vf');
