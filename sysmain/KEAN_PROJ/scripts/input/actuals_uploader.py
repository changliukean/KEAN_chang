import pandas as pd;
import os;
from pathlib import Path;
import sys;
import datetime;


SHEET_NAME_DICT = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby','HoldCo']};
ACTUALS_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/actuals';


sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller;
import db_controller_actuals;



def actuals_data_upload(conn_ins, company, scenario, last_amr_scenario=''):
    print ("=================   uploading actuals data to kean...");
    actuals_file_input_folder = ACTUALS_FILE_INPUT_FOLDER;
    actuals_input_file_list = os.listdir(actuals_file_input_folder);
    for actuals_file in actuals_input_file_list:
        full_file_path = os.path.join(actuals_file_input_folder, actuals_file);
        if company in full_file_path and '~' not in full_file_path and scenario in full_file_path:

            actuals_upload_list = read_actuals_xlsx(full_file_path,SHEET_NAME_DICT[company], scenario,company);

            """ before upload to kean, we TEST if the actuals data is consistent """
            if last_amr_scenario != '':
                check_actuals_data_consistency(conn_ins, company, last_amr_scenario, actuals_upload_list);
            # sys.exit();
            db_controller_actuals.upload_actuals_data(conn_ins, actuals_upload_list, scenario, company);


def read_actuals_xlsx(file_path, sheet_name_list, scenario, company):
    # print (file_path);
    print ("----------------------   reading excel inputs...");

    actuals_data = pd.read_excel(file_path, sheet_name_list, header = 0);

    total_actuals_upload_list = [];
    for item in actuals_data:
        current_tab_df = actuals_data[item];
        current_input_list = [];


        column_header_list = ['AS OF DATE','ACCOUNTING MONTH','BUSINESS UNIT ID','COMPANY NAME','BVR GROUP','ACCOUNT',\
                                                     'ACCOUNT TITLE','PROJECT ID', 'COST COMPONENT ID', 'WORK ORDER NUMBER', 'OUTAGE CODE ID',\
                                                     'INVOICE ID','CONTRACT NUMBER ID','REFERENCE NUMBER','PERIOD BALANCE', 'PLANT ID', 'REPORT_DATE',\
                                                     'ENDING BALANCE','TOTAL CREDIT','TOTAL DEBIT'];

        """ optimized logic I LOVE THIS!"""
        """ reduce the read time from 50 seconds to 20 sceonds!! """
        for column_header in column_header_list:
            current_input_list.append(list(current_tab_df[column_header]));


        scenario_list = [scenario for i in range(0, len(current_tab_df))];
        company_list = [company for i in range(0, len(current_tab_df))];

        current_input_list.append(scenario_list);
        current_input_list.append(company_list);

        current_input_list = [list(item) for item in zip(*current_input_list)];



        """ old logic """
        """ when the dataframe is big, iloc is not functioning efficiently """
        # for i in range(0, len(current_tab_df)):
        #     info_list = list(current_tab_df.iloc[i][['AS OF DATE','ACCOUNTING MONTH','BUSINESS UNIT ID','COMPANY NAME','BVR GROUP','ACCOUNT',\
        #                                              'ACCOUNT TITLE','PROJECT ID', 'COST COMPONENT ID', 'WORK ORDER NUMBER', 'OUTAGE CODE ID',\
        #                                              'INVOICE ID','CONTRACT NUMBER ID','REFERENCE NUMBER','PERIOD BALANCE', 'PLANT ID', 'REPORT_DATE',\
        #                                              'ENDING BALANCE','TOTAL CREDIT','TOTAL DEBIT']]);
        #
        #     info_list = info_list + [scenario, company];
        #     current_input_list.append(info_list);

        total_actuals_upload_list += current_input_list;
        # print (len(current_input_list));
        # for i in range(0, 10):
        #     print (current_input_list[i]);
        # sys.exit();
    return total_actuals_upload_list;



def check_actuals_data_consistency(conn_ins, company, last_amr_scenario, new_amr_actuals_upload_list):

    print ("----------------------   checking actuals data consistency...");

    last_amr_actuals_df = db_controller_actuals.get_actuals(conn_ins, company, last_amr_scenario);

    if len(last_amr_actuals_df) == 0:
        print ("No data for scenario: ", last_amr_scenario, " we directly load the actuals data.");
        return 0;

    date_range_list = list(set(list(last_amr_actuals_df['accounting_month'])));
    date_range_str_list = [str(item) for item in date_range_list];

    # print ("==========================================");
    #
    # for item in date_range_str_list:
    #     print (type(item));
    #
    # print ("==========================================");
    # print (new_amr_actuals_upload_list[0]);

    # print (str(new_amr_actuals_upload_list[0][1]).split(" ")[0] in date_range_str_list);

    print ("==========================================");
    print ("new actual data size: ", len(new_amr_actuals_upload_list));

    new_amr_actuals_upload_list_filtered = [item for item in new_amr_actuals_upload_list if str(item[1]).split(" ")[0] in date_range_str_list];
    print ("filtered new actual data size ",len(new_amr_actuals_upload_list_filtered));
    """ check sum of the four columns """
    """ 1. ending_balance """
    """ 2. period_balance """
    """ 3. total_debit """
    """ 4. total_credit """

    print ("==========================================");
    print (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[17] if str(item)!='nan']), sum(list(last_amr_actuals_df['ending_balance'])));
    ending_balance_checkflag = (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[17] if str(item)!='nan']) == sum(list(last_amr_actuals_df['ending_balance'])))
    print ("ending_balance_checkflag: ",ending_balance_checkflag);

    print ("==========================================");
    print (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[14] if str(item)!='nan']), sum(list(last_amr_actuals_df['period_balance'])));
    period_balance_checkflag = (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[14] if str(item)!='nan']) == sum(list(last_amr_actuals_df['period_balance'])))
    print ("period_balance_checkflag: ",period_balance_checkflag);

    print ("==========================================");
    print (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[19] if str(item)!='nan']), sum(list(last_amr_actuals_df['total_debit'])));
    total_debit_checkflag = (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[19] if str(item)!='nan']) == sum(list(last_amr_actuals_df['total_debit'])));
    print ("total_debit_checkflag: ",total_debit_checkflag);

    print ("==========================================");
    print (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[18] if str(item)!='nan']), sum(list(last_amr_actuals_df['total_credit'])));
    total_credit_checkflag = (sum([item for item in list(zip(*new_amr_actuals_upload_list_filtered))[18] if str(item)!='nan']) == sum(list(last_amr_actuals_df['total_credit'])));
    print ("total_credit_checkflag: ",total_credit_checkflag);


    """ one by one comparison """
    """ it will slow the procedure, do we really want it? """

    new_actuals_data_list = [[item[i] for i in [1,3,5,14,18,19]] for item in new_amr_actuals_upload_list_filtered]

    new_actuals_data_list = sorted(new_actuals_data_list, key=lambda x:x[0:2]);

    new_actuals_data_tuple_list = [];

    for item in new_actuals_data_list:
        item[0] = str(item[0]).split(" ")[0];
        item[1] = str(item[1]);
        item[2] = str(item[2]);
        item[3] = str(item[3]) if str(item[3])!='nan' else '0.0';
        item[4] = str(item[4]) if str(item[4])!='nan' else '0.0';
        item[5] = str(item[5]) if str(item[5])!='nan' else '0.0';
        new_actuals_data_tuple_list.append(tuple(item));

    # print ("==========================================");
    # for item in new_actuals_data_tuple_list[0:20]:
    #     print (item);
    # print ("==========================================");

    print (len(new_actuals_data_tuple_list));

    last_amr_actuals_data_df = last_amr_actuals_df[['accounting_month','entity','account','period_balance','total_credit','total_debit']];

    last_amr_actuals_data_list = [list(last_amr_actuals_data_df['accounting_month']),\
                                list(last_amr_actuals_data_df['entity']),\
                                list(last_amr_actuals_data_df['account']),\
                                list(last_amr_actuals_data_df['period_balance']),\
                                list(last_amr_actuals_data_df['total_credit']),\
                                list(last_amr_actuals_data_df['total_debit'])];


    last_amr_actuals_data_list = [list(item) for item in zip(*last_amr_actuals_data_list)];

    last_amr_actuals_data_list = sorted(last_amr_actuals_data_list, key=lambda x: x[0:2]);

    last_amr_actuals_data_tuple_list = [];

    for item in last_amr_actuals_data_list:
        item[0] = str(item[0]);
        item[3] = str(item[3]);
        item[4] = str(item[4]);
        item[5] = str(item[5]);
        last_amr_actuals_data_tuple_list.append(tuple(item));

    # #
    # print ("==========================================");
    # for item in last_amr_actuals_data_tuple_list[0:20]:
    #     print (item);
    # print ("==========================================");



    print (len(last_amr_actuals_data_list));


    """ this is too slow"""
    # diff_list = [diff_item for diff_item in new_actuals_data_list + last_amr_actuals_data_list if (diff_item not in last_amr_actuals_data_list) or (diff_item not in new_actuals_data_list)];



    diff_list_plus = list(set(tuple(new_actuals_data_tuple_list)) - set(tuple(last_amr_actuals_data_tuple_list)));


    diff_list_minus = list(set(tuple(last_amr_actuals_data_tuple_list)) - set(tuple(new_actuals_data_tuple_list)));
    print ("============================================================");
    print ("============ Difference between actuals data================");
    for item in diff_list_plus:
        print ('+ ', item);
    for item in diff_list_minus:
        print ('- ', item);
    print ("============================================================");

    if (not ending_balance_checkflag) or (not period_balance_checkflag) or (not total_debit_checkflag) or (not total_credit_checkflag) or (len(diff_list_plus+diff_list_minus) > 0):
        user_decision = input(" There are differences in actuals data between last scenario and this scenario, are you sure to upload? Y/N   ");
        if user_decision == "Y" or user_decision == 'y':
            print ("---------------------- Uploading actuals data to KEAN...");
        else:
            print ("---------------------- Quit")
            sys.exit();

    """ we cant do one by one comparison """
    """ it's too slow """
    # for item in new_amr_actuals_upload_list_filtered:
    #     """
    #         'AS OF DATE','ACCOUNTING MONTH','BUSINESS UNIT ID','COMPANY NAME','BVR GROUP','ACCOUNT',\
    #                                                  'ACCOUNT TITLE','PROJECT ID', 'COST COMPONENT ID', 'WORK ORDER NUMBER', 'OUTAGE CODE ID',\
    #                                                  'INVOICE ID','CONTRACT NUMBER ID','REFERENCE NUMBER','PERIOD BALANCE', 'PLANT ID', 'REPORT_DATE',\
    #                                                  'ENDING BALANCE','TOTAL CREDIT','TOTAL DEBIT'
    #
    #     """
    #     cur_business_unit_id = item[2];
    #     cur_accounting_month = item[1];
    #     cur_bvr_group = item[4];
    #     cur_account = item[5];
    #     cur_account_title = item[6];
    #     cur_project_id = item[7];
    #     cur_cost_component_id = item[8];
    #     cur_work_order_number = item[9];
    #     cur_outage_code_id = item[10];
    #     cur_invoice_id = item[11];
    #     cur_contract_number_id = item[12];
    #     cur_reference_number = item[13];
    #     cur_plant_id = item[15];
    #
    #     cur_business_unit_id = str(cur_business_unit_id) if str(cur_business_unit_id) != 'nan' else '';
    #     cur_accounting_month = datetime.datetime.strptime(str(cur_accounting_month).split(" ")[0],"%Y-%m-%d").date();
    #     cur_bvr_group = str(cur_bvr_group) if str(cur_bvr_group) != 'nan' else '';
    #     cur_account = str(cur_account) if str(cur_account) != 'nan' else '';
    #     cur_account_title = str(cur_account_title) if str(cur_account_title) != 'nan' else '';
    #     cur_project_id = str(cur_project_id) if str(cur_project_id) != 'nan' else '';
    #     cur_cost_component_id = str(cur_cost_component_id) if str(cur_cost_component_id) != 'nan' else 0;
    #     cur_outage_code_id = str(cur_outage_code_id) if str(cur_outage_code_id) != 'nan' else '';
    #     cur_invoice_id = str(cur_invoice_id) if str(cur_invoice_id) != 'nan' else '';
    #     cur_contract_number_id = str(cur_contract_number_id) if str(cur_contract_number_id) != 'nan' else '';
    #     cur_reference_number = str(cur_reference_number) if str(cur_reference_number) != 'nan' else '';
    #     # print (type(cur_cost_component_id), cur_cost_component_id);
    #     cur_plant_id = str(cur_plant_id) if str(cur_plant_id) != 'nan' else '';
    #
    #     # print (type(last_amr_actuals_df.iloc[0]['cost_component']), last_amr_actuals_df.iloc[0]['cost_component']);
    #
    #     item_in_actuals_df = last_amr_actuals_df.loc[(last_amr_actuals_df['business_unit_id']==cur_business_unit_id) &\
    #                                                  (last_amr_actuals_df['accounting_month']==cur_accounting_month) &\
    #                                                  (last_amr_actuals_df['bvr_group']==cur_bvr_group) &\
    #                                                  (last_amr_actuals_df['account']==cur_account) &\
    #                                                  (last_amr_actuals_df['account_title']==cur_account_title) &\
    #                                                  (last_amr_actuals_df['project_id']==cur_project_id) &\
    #                                                  (last_amr_actuals_df['cost_component']==cur_cost_component_id) &\
    #                                                  (last_amr_actuals_df['work_order_number']==cur_work_order_number) &\
    #                                                  (last_amr_actuals_df['outage_code']==cur_outage_code_id) &\
    #                                                  (last_amr_actuals_df['invoice_id']==cur_invoice_id) &\
    #                                                  (last_amr_actuals_df['contract_number']==cur_contract_number_id) &\
    #                                                  (last_amr_actuals_df['reference_number']==cur_reference_number) &\
    #                                                  (last_amr_actuals_df['plant_id']==cur_plant_id)];
    #     print (len(item_in_actuals_df));
