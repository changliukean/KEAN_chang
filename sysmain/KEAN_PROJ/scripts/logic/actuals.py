from pathlib import Path;
import sys;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_actuals;
import db_controller;

import datetime;


COMPANY_ENTITY_DICT= {'Lightstone':['Gavin Power LLC','Waterford Energy Center','Lawrenceburg Generating Station', 'Darby Electric Generating Station']}

COMPANY_HOLDCO_DICT = {'Lightstone':['Lightstone Generation LLC','Lightstone Marketing LLC']};


TB_ORDER_LIST = ["ENG","COMFUEL","EMSNEXP","VARONM","FXDFUELTRANS",\
                          "CAPPAY","ASR",\
                          "OTHREVN","FXDLABEXP","MANTPARTS","OPERATIONS","ENVSAFTY",\
                          "FUELHAND","PRPTYTAX","INSURANCE","MANTTOTAL","ENVTOTAL",\
                          "LTSATOTAL","GROWTHTOTAL"]

ACCOUNT_MAPPING_DICT = {  "ENG":["Energy Revenue",1],"COMFUEL":["Delivered Fuel Expense",-1],\
                          "EMSNEXP":["Net Emissions Expense",-1],\
                          "VARONM":["Variable O&M Expense",-1],"FXDFUELTRANS":["Fixed Fuel",-1],\
                          "CAPPAY":["Capacity Revenue",1],"ASR":["Ancillary Services Revenue",1],\
                          "OTHREVN":["Misc Income",1],"FXDLABEXP":["Labor Expenses",-1],\
                          "MANTPARTS":["Maintenance",-1],\
                          "OPERATIONS":["Operations",-1],"ENVSAFTY":["Removal Costs",-1],\
                          "FUELHAND":["Fuel Handling",-1],"PRPTYTAX":["Property Tax",-1],\
                          "INSURANCE":["Insurance",-1],\
                          "MANTTOTAL":["Maintenance Capex",1],"ENVTOTAL":["Environmental Capex",1],\
                          "LTSATOTAL":["LTSA Capex",1],"GROWTHTOTAL":["Growth Capex",1], "HEDGEPL":["Hedge P&L",1]};



def actuals_main(conn_ins, company, amr_scenario, actuals_month_dates_list):
    print ("=================   calculating actuals financials results...");
    entity_name_list = COMPANY_ENTITY_DICT[company];
    accounting_month_list = actuals_month_dates_list;

    upload_to_financials_list = [];




    for entity_name in entity_name_list:
        comparison_result_dict_total = get_actuals_result(conn_ins, company, entity_name, amr_scenario, accounting_month_list);

        for accounting_month in accounting_month_list:
            # print ("=======================================");
            comparison_result_dict = comparison_result_dict_total[accounting_month];
            for item in TB_ORDER_LIST:
                upload_to_financials_list.append([company, entity_name.split(" ")[0], amr_scenario, ACCOUNT_MAPPING_DICT[item][0], accounting_month, comparison_result_dict[item][0] * ACCOUNT_MAPPING_DICT[item][1]])
            # print ("=======================================");

            energy_margin = 0.0;
            total_other_income = 0.0;
            net_energy_margin = 0.0;
            gross_margin = 0.0;
            fixed_non_labor = 0.0;
            general_and_admin = 0.0;
            total_fixed_costs = 0.0;
            ebidta = 0.0;
            total_capex = 0.0;
            cf_debt = 0.0;
            ebidta_less_total_capex = 0.0;
            hedgepnl = 0.0;

            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Gross Energy Margin" , accounting_month, energy_margin])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Total Other Income", accounting_month, total_other_income])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Gross Margin", accounting_month, gross_margin])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Fixed Non-Labor Expense", accounting_month, fixed_non_labor])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "General & Administrative", accounting_month, general_and_admin])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Total Fixed Costs", accounting_month, total_fixed_costs])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "EBITDA", accounting_month, ebidta])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Total Capex", accounting_month, total_capex])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "EBITDA less Capex", accounting_month, ebidta_less_total_capex])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Net Energy Margin", accounting_month, net_energy_margin])
            upload_to_financials_list.append([company, entity_name.split(" ")[0],  amr_scenario, "Hedge P&L", accounting_month, hedgepnl])

    print (len(upload_to_financials_list));
    db_controller.upload_cal_results_to_financials(conn_ins, upload_to_financials_list,company, amr_scenario);


    """ holdco actuals has a separate function, cuz the logics between holdco and power plants are different """
    """ modulizing this part can make trouble shooting easier """
    actuals_holdco_main(conn_ins, company, amr_scenario, actuals_month_dates_list);

def actuals_holdco_main(conn_ins, company, amr_scenario, actuals_month_dates_list):


    entity_name_list = COMPANY_HOLDCO_DICT[company];
    accounting_month_list = actuals_month_dates_list;
    upload_to_financials_list = [];



    order_list = ["HEDGEPL","ARCTOSAMA","KINDLEAMA","NEXTEMA","CAMSOMA","TRANSCOST"]

    holdco_mapping_dict = {"CAMSOMA":"CAMS (OMA fees)","TRANSCOST":"Transition Costs","KINDLEAMA":"Kindle Energy (AMA fees)",
    "HEDGEPL":"Hedge P&L","ARCTOSAMA":"Arctos","NEXTEMA":"Nextera (EMA fees)"};


    result_value_dict = {};

    for accounting_month in accounting_month_list:
        result_value_dict[accounting_month] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0];

    for entity_name in entity_name_list:
        comparison_result_dict_total = get_actuals_result_holdco(conn_ins, company, entity_name, amr_scenario, accounting_month_list);

        for accounting_month in accounting_month_list:
            comparison_result_dict = comparison_result_dict_total[accounting_month];
            # print ("=======================================");
            value_list = [];
            for item in order_list:
                if item in comparison_result_dict and len(comparison_result_dict[item]) > 0:
                    value_list.append(comparison_result_dict[item][0]);
                    if item in ["ARCTOSAMA","KINDLEAMA","NEXTEMA","CAMSOMA","TRANSCOST"]:
                        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, holdco_mapping_dict[item] , accounting_month, -comparison_result_dict[item][0]])


            hedge_pnl = value_list[0];
            gen_admin = -sum(value_list[1:6]);



            net_energy_margin = 0.0;
            gross_margin = 0.0;
            total_fixed_costs = 0.0;

            ebitda = 0.0;

            ebitda_less_total_capex = 0.0;

            # print (accounting_month, "   ", hedge_pnl, "   ", gen_admin);


            result_value_dict[accounting_month][0] += hedge_pnl;
            result_value_dict[accounting_month][1] += gen_admin;
            result_value_dict[accounting_month][2] += gross_margin;
            result_value_dict[accounting_month][3] += net_energy_margin;
            result_value_dict[accounting_month][4] += total_fixed_costs;
            result_value_dict[accounting_month][5] += ebitda;
            result_value_dict[accounting_month][6] += ebitda_less_total_capex;



    for accounting_month in accounting_month_list:
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "Hedge P&L" , accounting_month, result_value_dict[accounting_month][0]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "General & Administrative", accounting_month, result_value_dict[accounting_month][1]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "Gross Margin", accounting_month, result_value_dict[accounting_month][2]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "Net Energy Margin", accounting_month, result_value_dict[accounting_month][3]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "Total Fixed Costs", accounting_month, result_value_dict[accounting_month][4]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "EBITDA", accounting_month, result_value_dict[accounting_month][5]])
        upload_to_financials_list.append([company, 'HoldCo',  amr_scenario, "EBITDA less Capex", accounting_month, result_value_dict[accounting_month][6]])


    db_controller.upload_cal_results_to_financials(conn_ins, upload_to_financials_list, company ,amr_scenario);



def get_actuals_result_holdco(conn_ins, company_name, entity_name, scenario, accounting_month_list):
    plant_id,\
    bvr_mapping_df_groupby_fsli,\
    actuals_df = prepare_data_actuals(conn_ins, company_name, entity_name, scenario);

    bvr_result_list = [];
    fsli_group = bvr_mapping_df_groupby_fsli.groups;



    comparison_result_dict_total = {};


    for accounting_month in accounting_month_list:
        accounting_month_obj = date_utils.get_date_from_str(accounting_month);
        comparison_result_dict = {"HEDGEPL":[],"ARCTOSAMA":[],"KINDLEAMA":[],"NEXTEMA":[],"CAMSOMA":[],\
                          "TRANSCOST":[],"GENADMN":[],\
                          "OTHREVN":[],"FXDLABEXP":[],"MANTPARTS":[],"OPERATIONS":[],"ENVSAFTY":[],\
                          "FUELHAND":[],"PRPTYTAX":[],"INSURANCE":[],"MANTTOTAL":[],"ENVTOTAL":[],\
                          "LTSATOTAL":[],"GROWTHTOTAL":[]};
        current_actuals_df = actuals_df.loc[actuals_df['accounting_month']==accounting_month_obj];


        for fsli_item in fsli_group:
            fsli_info_df = bvr_mapping_df_groupby_fsli.get_group(fsli_item);
            account_list = [];
            for i in range(0, len(fsli_info_df)):
                account_list.append(fsli_info_df.iloc[i]['account']);


            account_data_df = current_actuals_df.loc[(current_actuals_df['account'].isin(account_list))][['account','total_credit', 'total_debit','period_balance']];


            account_not_found_list = [account_item for account_item in account_list if account_item not in list(account_data_df['account'])];
            credit_sign = fsli_info_df.iloc[0]['credit_sign'];
            debit_sign = fsli_info_df.iloc[0]['debit_sign'];
            sumup_value = 0.0;
            if len(account_data_df) > 0:
                for i in range(0, len(account_data_df)):
                    # print (credit_sign * account_data_df.iloc[i]['total_credit'], debit_sign * account_data_df.iloc[i]['total_debit']);
                    if 'C' not in account_data_df.iloc[i]['account']:
                        sumup_value += credit_sign * account_data_df.iloc[i]['total_credit'];
                        sumup_value += debit_sign * account_data_df.iloc[i]['total_debit'];
                    else:
                        sumup_value += account_data_df.iloc[i]['period_balance'];

            comparison_result_dict[fsli_item] = [round(sumup_value,10), account_not_found_list];
        comparison_result_dict_total[accounting_month] = comparison_result_dict;
    return comparison_result_dict_total;



def prepare_data_actuals(conn_ins, company_name, entity_name, scenario):
    plant_id = db_controller_actuals.get_entity_plant_id(conn_ins, entity_name);
    print (plant_id);

    mapping_effective_date = date_utils.get_date_by_scenario(scenario);

    # print (mapping_effective_date);

    tb_mapping_df_groupby_fsli = db_controller_actuals.get_tb_mapping(conn_ins, company_name, plant_id);

    actuals_df = db_controller_actuals.get_actuals(conn_ins, company_name, scenario, entity_name);
    # print (len(actuals_df));

    return plant_id, tb_mapping_df_groupby_fsli, actuals_df;


def get_actuals_result(conn_ins, company_name, entity_name, scenario, accounting_month_list):
    # print ("here we are!");
    # print (company_name);
    # print (entity_name);
    # print (input_date);
    plant_id,\
    tb_mapping_df_groupby_fsli,\
    actuals_df = prepare_data_actuals(conn_ins, company_name, entity_name, scenario);


    bvr_result_list = [];
    fsli_group = tb_mapping_df_groupby_fsli.groups;



    comparison_result_dict_total = {};

    for accounting_month in accounting_month_list:
        # print (accounting_month);


        accounting_month_obj = date_utils.get_date_from_str(accounting_month);
        comparison_result_dict = {"ENG":[],"COMFUEL":[],"EMSNEXP":[],"VARONM":[],"FXDFUELTRANS":[],\
                          "CAPPAY":[],"ASR":[],\
                          "OTHREVN":[],"FXDLABEXP":[],"MANTPARTS":[],"OPERATIONS":[],"ENVSAFTY":[],\
                          "FUELHAND":[],"PRPTYTAX":[],"INSURANCE":[],"MANTTOTAL":[],"ENVTOTAL":[],\
                          "LTSATOTAL":[],"GROWTHTOTAL":[]};

        current_actuals_df = actuals_df.loc[actuals_df['accounting_month']==accounting_month_obj];
        # print (current_actuals_df);
        # print ("!!!!!!!!!!!!!!!!!!!!!!!!!",len(current_actuals_df));

        for fsli_item in fsli_group:
            # print (fsli_item);
            fsli_info_df = tb_mapping_df_groupby_fsli.get_group(fsli_item);
            accounting_month_obj = datetime.datetime.strptime(accounting_month, '%Y-%m-%d').date();
            fsli_info_df = fsli_info_df.loc[(fsli_info_df['effective_start_date'] <= accounting_month_obj) & (fsli_info_df['effective_end_date'] >= accounting_month_obj)];

            account_list = [];
            for i in range(0, len(fsli_info_df)):
                account_list.append(fsli_info_df.iloc[i]['account']);

            account_data_df = current_actuals_df.loc[(current_actuals_df['account'].isin(account_list))][['account','total_credit', 'total_debit','period_balance']];



            account_not_found_list = [account_item for account_item in account_list if account_item not in list(account_data_df['account']) ];
            credit_sign = fsli_info_df.iloc[0]['credit_sign'];
            debit_sign = fsli_info_df.iloc[0]['debit_sign'];
            sumup_value = 0.0;
            if len(account_data_df) > 0:
                for i in range(0, len(account_data_df)):
                    # if fsli_item == 'COMFUEL' and entity_name == 'Gavin Power LLC' and accounting_month == '2017-07-31':
                    #     print (account_data_df.iloc[i]['account'],'\t',credit_sign * account_data_df.iloc[i]['total_credit']+debit_sign * account_data_df.iloc[i]['total_debit'] ,'\t', entity_name);

                    if 'C' not in account_data_df.iloc[i]['account']:
                        sumup_value += credit_sign * account_data_df.iloc[i]['total_credit'];
                        sumup_value += debit_sign * account_data_df.iloc[i]['total_debit'];
                    else:
                        sumup_value += account_data_df.iloc[i]['period_balance'];

            comparison_result_dict[fsli_item] = [round(sumup_value,10), account_not_found_list];
        comparison_result_dict_total[accounting_month] = comparison_result_dict;
    return comparison_result_dict_total;
