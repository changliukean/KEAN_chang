from pathlib import Path;
import sys;
import datetime;

sys.path.insert(0, str(Path(__file__).parents[1])+r'\utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'\database');
import db_controller_budget;
import db_controller_respreads;
import db_controller_actuals;
import db_controller;




import pandas as pd;

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






def respreads_main_details(conn_ins, company, amr_scenario, budget_scenario, respreads_period_range_list):


    """ step 1: prepare data """

    budget_df = db_controller_budget.get_budget_data(conn_ins, company, budget_scenario, respreads_period_range_list);
    respreads_df = db_controller_respreads.get_respreads(conn_ins, company, amr_scenario);
    actuals_df = db_controller_actuals.get_actuals(conn_ins, company, amr_scenario);



    actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario);

    actuals_start_date = datetime.datetime.strptime(actuals_month_dates_list[0], '%Y-%m-%d').date();
    actuals_end_date = datetime.datetime.strptime(actuals_month_dates_list[-1], '%Y-%m-%d').date();
    estimate_start_date = datetime.datetime.strptime(estimate_month_dates_list[0], '%Y-%m-%d').date();
    estimate_end_date = datetime.datetime.strptime(estimate_month_dates_list[-1], '%Y-%m-%d').date();


    """ step 2: get ytd variance view """

    actual_plant_id_list = list(set(list(actuals_df['plant_id'])));

    # print (actual_plant_id_list);


    actuals_plant_fsli_account_list = [];
    for plant_id in actual_plant_id_list:
        fsli_mapping_df = db_controller_budget.get_tb_mapping_company(conn_ins, company, estimate_month_dates_list[0], plant_id);
        for fsli in fsli_mapping_df.groups:
            fsli_account_mapping_df = fsli_mapping_df.get_group(fsli);
            for i in range(0, len(fsli_account_mapping_df)):
                actuals_plant_fsli_account_list.append(list(fsli_account_mapping_df.iloc[i][['plant_id','fsli','account']]));


    actuals_ytd_list = [];
    for item in actuals_plant_fsli_account_list:
        # print (item);
        actuals_plant_fsli_account_project_df = actuals_df.loc[(actuals_df['plant_id']==item[0]) & (actuals_df['account']==item[2])];
        grouped_actuals_plant_fsli_account_project_df = actuals_plant_fsli_account_project_df.groupby(['account','project_id']);
        for account_project_group in grouped_actuals_plant_fsli_account_project_df.groups:
            account_project_df = grouped_actuals_plant_fsli_account_project_df.get_group(account_project_group);
            if 'C' != account_project_group[0][0]:
                ytd_actuals_value = sum(list(account_project_df['total_credit'])) - sum(list(account_project_df['total_debit']));
            else:
                ytd_actuals_value = -sum(list(account_project_df['period_balance']))

            actuals_ytd_list.append(['Actual',item[0],item[0],item[1],account_project_group[0],account_project_group[1],ytd_actuals_value]);

    print ("Actuals plant fsli account list length: ",len(actuals_plant_fsli_account_list));




    # for item in actuals_ytd_list:
    #     print (item);
    print ("Actuals YTD list length: ", len(actuals_ytd_list));

    # sys.exit();


    budget_entity_fsli_account_list = [];

    budget_entity_list = list(set(list(budget_df['entity'])));

    budget_plant_id_list = [[db_controller_budget.get_entity_plant_id(conn_ins, item), item] for item in budget_entity_list];

    # print (budget_plant_id_list);

    budget_plant_fsli_account_list = [];
    for plant_id in budget_plant_id_list:
        # print (plant_id);
        fsli_mapping_df = db_controller_budget.get_tb_mapping_company(conn_ins, company,  estimate_month_dates_list[0], plant_id[0]);
        for fsli in fsli_mapping_df.groups:
            fsli_account_mapping_df = fsli_mapping_df.get_group(fsli);
            for i in range(0, len(fsli_account_mapping_df)):
                budget_plant_fsli_account_list.append([plant_id[1]]+list(fsli_account_mapping_df.iloc[i][['plant_id','fsli','account']]));

    print ("Budget plant fsli account list length: ",len(budget_plant_fsli_account_list));

    # for item in budget_plant_fsli_account_list:
    #     print (item);



    budget_ytd_list = [];
    for item in budget_plant_fsli_account_list:
        # print (item);
        budget_plant_fsli_account_project_df = budget_df.loc[(budget_df['entity']==item[0]) & (budget_df['account']==item[3])];
        grouped_budget_plant_fsli_account_project_df = budget_plant_fsli_account_project_df.groupby(['account','project_id']);
        for account_project_group in grouped_budget_plant_fsli_account_project_df.groups:
            account_project_df = grouped_budget_plant_fsli_account_project_df.get_group(account_project_group);

            ytd_budget_value = sum(list(account_project_df.loc[account_project_df['period'] <= actuals_end_date]['value']));


            budget_ytd_list.append(['Budget',item[0],item[1],item[2],account_project_group[0],account_project_group[1],ytd_budget_value]);

    print ("Budget plant fsli account list length: ",len(budget_plant_fsli_account_list));

    # for item in budget_ytd_list:
    #     print (item);

    print ("Budget YTD list length: ", len(budget_ytd_list));

    ytd_result_list = actuals_ytd_list + budget_ytd_list;

    ytd_df = pd.DataFrame(data = ytd_result_list, columns = ['source','entity','plant_id','fsli','account','project_id','ytd_value']);

    # ytd_df.to_csv('ytd_df.csv');


    ytd_variance_list = [];

    for actual_item in actuals_ytd_list:
        flag = 0;
        for budget_item in budget_ytd_list:
            # print (actual_item[2:6]);
            if actual_item[2:6] == budget_item[2:6]:
                ytd_variance_list.append(actual_item[2:6]+[actual_item[6], budget_item[6], actual_item[6] - budget_item[6]]+['acc-proj combo exists in both Actual and Budget']);
                flag = 1;
        if flag == 0:
            """ we have actuals but no budget """
            ytd_variance_list.append(actual_item[2:6] + [actual_item[6], 0, actual_item[6]-0, 'acc-proj combo only exists in actual']);

    for budget_item in budget_ytd_list:
        flag = 0;
        for actual_item in actuals_ytd_list:
            if actual_item[2:6] == budget_item[2:6]:
                flag = 1;
        if flag == 0:
            """ we have budget but no actuals """
            ytd_variance_list.append(budget_item[2:6] + [0, budget_item[6], 0 - budget_item[6], 'acc-proj combo only exists in budget']);


    print (len(ytd_variance_list));

    ytd_variance_list = sorted(ytd_variance_list, key = lambda x: (x[0],x[1],x[2],x[3]));


    ytd_variance_df = pd.DataFrame(data = ytd_variance_list, columns = ['entity','fsli','account','project','ytd actual', 'ytd budget', 'ytd variance','note']);
    ytd_variance_df.to_csv('ytd_variance_df.csv');


    """ step 3: get targeted respreads """

    respreads_entity_list = list(set(list(respreads_df['entity'])));

    # print ("=================================");
    # print (respreads_entity_list);
    # print ("=================================");

    respreads_plant_id_list = [[db_controller_budget.get_entity_plant_id(conn_ins, item), item] for item in respreads_entity_list];

    print (respreads_plant_id_list);

    respreads_plant_fsli_account_list = [];
    for plant_id in respreads_plant_id_list:
        # print (plant_id);
        fsli_mapping_df = db_controller_budget.get_tb_mapping_company(conn_ins, company,  estimate_month_dates_list[0],plant_id[0]);
        for fsli in fsli_mapping_df.groups:
            fsli_account_mapping_df = fsli_mapping_df.get_group(fsli);
            for i in range(0, len(fsli_account_mapping_df)):
                respreads_plant_fsli_account_list.append([plant_id[1]]+list(fsli_account_mapping_df.iloc[i][['plant_id','fsli','account']]));

    print ("Respreads plant fsli account list length: ",len(respreads_plant_fsli_account_list));

    # for item in respreads_plant_fsli_account_list:
    #     print (item);


    # for item in budget_ytd_list:
    #     print (item);

    targeted_respreads_list = [];

    for i in range(0, len(respreads_df)):
        current_entity = respreads_df.iloc[i]['entity'];
        current_account = respreads_df.iloc[i]['account'];
        current_project_id = respreads_df.iloc[i]['project_id'];
        current_period = respreads_df.iloc[i]['period'];
        current_value = respreads_df.iloc[i]['value'];

        current_plant_fsli = [item[1:3] for item in respreads_plant_fsli_account_list if item[0] == current_entity and item[3] == current_account][0];

        current_budget = 0.0;
        current_actuals = 0.0;

        current_budget_df = budget_df.loc[(budget_df['period'] == current_period) & (budget_df['entity'] == current_entity) & (budget_df['account'] == current_account) & (budget_df['project_id'] == current_project_id)];
        if not current_budget_df.empty:
            current_budget = current_budget_df.iloc[0]['value'];

        targeted_respreads_list.append([current_entity, current_plant_fsli[0], current_plant_fsli[1], current_account, current_project_id, current_period, current_value, current_budget, current_budget + current_value]);

    print ("Targeted respreades length: ",len(targeted_respreads_list));


    targeted_respreads_list = sorted(targeted_respreads_list, key = lambda x: (x[0],x[2],x[3],x[4],x[5]));

    targeted_respreads_df = pd.DataFrame(data = targeted_respreads_list, columns = ['entity','plant_id','fsli','account','project','period','targeted respreads value','budget','budget + target resp']);

    targeted_respreads_df.to_csv("targeted_respreads_df.csv");



    """ step 4: get peanut butter respreads view """


    level_respreads_list = [];

    plant_id_entity_dict = {'DBY001':'Darby','LMC001':'HoldCo','LSHLD001':'HoldCo','WAT001':'Waterford','LWS001':'Lawrenceburg','GPW001':'Gavin'}

    for ytd_var_item in ytd_variance_list:
        flag = 0;
        for targeted_item in targeted_respreads_list:
            """ if the acc-proj combo already exists in targeted respreads list, we don't do any peanut butter respreads on that """
            target_project_id = targeted_item[4] if targeted_item[4]!='nan' else '';

            if ytd_var_item[0] == targeted_item[1] and ytd_var_item[1] == targeted_item[2] and ytd_var_item[2] == targeted_item[3] and ytd_var_item[3] == target_project_id:
                flag = 1;
        if flag == 0:
            pb_respreads_value = ytd_var_item[6]/ len(estimate_month_dates_list);

            for estimate_date in estimate_month_dates_list:
                estimate_date_obj = datetime.datetime.strptime(estimate_date, "%Y-%m-%d").date();
                # print (plant_id_entity_dict[ytd_var_item[0]], ytd_var_item[2], ytd_var_item[3],estimate_date_obj);
                current_budget_df = budget_df.loc[(budget_df['entity']==plant_id_entity_dict[ytd_var_item[0]]) & (budget_df['account']==ytd_var_item[2]) & (budget_df['project_id']==ytd_var_item[3]) & (budget_df['period'] == estimate_date_obj) ];
                # print (len(current_budget_df));
                # sys.exit();
                current_value = 0.0;
                note = 'acc-proj combo doenst exist in budget, need addition'
                if not current_budget_df.empty:
                    current_value = current_budget_df.iloc[0]['value'];
                    note = 'acc-proj combo exists in budget';

                level_respreads_list.append([plant_id_entity_dict[ytd_var_item[0]]] + ytd_var_item[0:4]+[str(estimate_date_obj),current_value,pb_respreads_value,current_value+pb_respreads_value,note]);

    # for item in level_respreads_list:
        # print (item);

    level_respreads_list = sorted(level_respreads_list, key = lambda x: (x[0],x[1],x[2],x[3],x[4]));

    level_respreads_df = pd.DataFrame(data = level_respreads_list, columns = ['entity','plant_id','fsli','account','project','period','budget','pb respreads','budget + pb respreads','note']);

    level_respreads_df.to_csv("level_respreads_df.csv");

    """ step 5: get a summurized projects detail view of peanut butter respreads and targeted respreads """
    respreads_summary_list = [];

    for item in targeted_respreads_list:
        current_project_id = item[4] if item[4] != 'nan' else '';
        respreads_summary_list.append(item[0:4] + [current_project_id] + [item[5]] + [item[7]]+[item[6]]+[item[8]]+['targeted respreads']);

    for item in level_respreads_list:
        respreads_summary_list.append(item[0:6]+[item[6]]+[item[7]]+[item[8]]+['peanut butter respreads']);

    respreads_summary_df = pd.DataFrame(data = respreads_summary_list, columns = ['entity','plant_id','fsli','account','project','period','budget','adj','forecast','type']);


    print ("Respreads summary list length: ", len(respreads_summary_list));
    respreads_summary_df.to_csv("respreads_summary_df.csv");


    add_budget_list = [];
    id_start = budget_df['id_budget'].max()+1;
    for respreads_item in respreads_summary_list:


        current_period_obj = datetime.datetime.strptime(respreads_item[5],'%Y-%m-%d').date() if isinstance(respreads_item[5], str) else respreads_item[5];

        # print (current_period_obj, type(current_period_obj));

        adj_budget_df = budget_df.loc[(budget_df['entity'] == respreads_item[0]) & (budget_df['account'] == respreads_item[3]) & (budget_df['project_id'] == respreads_item[4]) & (budget_df['period'] == current_period_obj)];

        if not adj_budget_df.empty:
            current_id_in_budget = adj_budget_df.iloc[0]['id_budget'];
            current_value = adj_budget_df.iloc[0]['value'];
            if 'targeted' in respreads_item[-1]:
                budget_df.loc[budget_df.id_budget == current_id_in_budget,'value'] = current_value + respreads_item[7];
            else:
                budget_df.loc[budget_df.id_budget == current_id_in_budget,'value'] = current_value - respreads_item[7];

        else:
            if 'targeted' in respreads_item[-1]:
                add_budget_list.append([id_start, company, budget_scenario, respreads_item[0], respreads_item[3], '', current_period_obj, respreads_item[7], '', respreads_item[4],
                                                        '','','','','','','','','']);
            else:
                add_budget_list.append([id_start, company, budget_scenario, respreads_item[0], respreads_item[3], '', current_period_obj, -respreads_item[7], '', respreads_item[4],
                                                        '','','','','','','','','']);
            id_start += 1;
        # budget_df.loc[budget_df.id_budget == current_id_in_budget,'value'] = new_value;


    add_budget_df = pd.DataFrame(data = add_budget_list, columns = budget_df.columns);

    print ('before:',len(budget_df));
    budget_df = budget_df.append(add_budget_df);
    print ('after:',len(budget_df));


    budget_df.to_csv('temp_budget.csv');
    # sys.exit();

    respreads_financial_upload_list = get_budget_financials_respreads(conn_ins, budget_df, estimate_month_dates_list, company, amr_scenario);

    for item in respreads_financial_upload_list:
        print (item);

    db_controller.upload_cal_results_to_financials(conn_ins, respreads_financial_upload_list, company, amr_scenario);



def get_budget_financials_respreads(conn_ins, budget_df, date_range_list, company_name, scenario):
    print ("=================   calculating budget respreaded financials results...");

    budget_financials_result_list = [];
    grouped_budget_df = budget_df.groupby(['entity']);


    # grouped_budget_df.get_group('Darby').to_csv("grouped_budget_df.csv");

    month_str = str(date_utils.get_month_number(scenario.split(" ")[1])) if len(str(date_utils.get_month_number(scenario.split(" ")[1]))) > 1 else '0'+str(date_utils.get_month_number(scenario.split(" ")[1]));

    data_date = scenario.split(" ")[0] + "-" + month_str + '-01';
    print (data_date);



    ACCOUNT_MAPPING_DICT = {  "Maintenance":-1,\
                              "Operations":-1,"Removal Costs":-1,\
                              "Fuel Handling":-1,\
                              "Maintenance Capex":-1,"Environmental Capex":-1,"General & Administrative":-1,"Growth Capex":-1};



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
                if financials_account in ACCOUNT_MAPPING_DICT:
                    budget_financials_result_list.append([company_name, entity_name, scenario, financials_account, period, ACCOUNT_MAPPING_DICT[financials_account] * fsli_value]);

                if financials_account in ["CAMS (OMA fees)","Transition Costs","Kindle Energy (AMA fees)",\
                          "Arctos","Nextera (EMA fees)"]:
                    # for i in range(0, len(current_budget_df)):
                    #     print (list(current_budget_df.iloc[i][['entity','account','project_id','period','value']]));
                    # print (entity_name, period, financials_account, fsli_value);
                    general_and_admin += fsli_value;


            budget_financials_result_list.append([company_name, entity_name, scenario, "General & Administrative", period, -general_and_admin])
    return budget_financials_result_list;
