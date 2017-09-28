import csv;
import datetime;
import sys;
import os;
from pathlib import Path;
import pandas as pd;



sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_budget;

BUDGET_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/budget';


def budget_data_upload(conn_ins, company, budget_scenario):
    """ Refactoring """
    print ("=================   uploading budget data to kean...");
    budget_file_input_folder = BUDGET_FILE_INPUT_FOLDER;
    budget_input_file_list = os.listdir(budget_file_input_folder);
    for budget_file in budget_input_file_list:
        full_file_path = os.path.join(budget_file_input_folder, budget_file);
        if company in full_file_path and '~' not in full_file_path:
            print (full_file_path);
            budget_upload_list = read_budget_input(full_file_path, company, budget_scenario);
            print (len(budget_upload_list));
            # sys.exit();
            db_controller_budget.upload_budget_data(conn_ins, budget_upload_list, budget_scenario, company);


    return 0;




def read_budget_input(budget_input_file_path, company_name, budget_scenario):
    print ("----------------------   reading excel inputs...");
    budget_data_df = pd.read_excel(budget_input_file_path, header = 0);
    print (len(budget_data_df));

    budget_info_header_list = ['Plant','Account No','Account Title','Model group','Project ID','Cost Component ID',\
                               'Work Order Number','Outage Code ID','Invoice ID','Contract Number ID',\
                               'Reference number','Cost Category','Cost Sub Category','Project Name'];

    budget_info_list = [];
    for budget_info_header_item in budget_info_header_list:
        budget_info_list.append(budget_data_df[budget_info_header_item]);

    budget_info_list = [list(item) for item in zip(*budget_info_list)];


    # print (len(budget_info_list));
    #
    # for item in budget_info_list:
    #     print (item);

    budget_upload_list = [];

    for i in range(len(budget_info_header_list), len(budget_data_df.columns)-1):
        # print (list(budget_data_df.columns)[i]);
        # print (len(budget_data_df[list(budget_data_df.columns)[i]]));

        scenario_list = [budget_scenario for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        company_list = [company_name for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        period_list = [str(list(budget_data_df.columns)[i]).split(" ")[0] for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        value_list = list(budget_data_df[list(budget_data_df.columns)[i]]);

        temp_combine_list = [scenario_list, company_list, period_list, value_list];
        temp_combine_list = [list(item) for item in zip(*temp_combine_list)];

        temp_budget_upload_list = [list(item_a + item_b) for item_a, item_b in zip(budget_info_list, temp_combine_list)];

        # print (len(temp_budget_upload_list));

        budget_upload_list += temp_budget_upload_list;

    return budget_upload_list;


def read_budget_input_old(file_path, company_name, data_date):
    with open(file_path, 'r') as f:
        reader = csv.reader(f);
        budget_list = list(reader);

    period_range = budget_list[0][14:];

    reformat_period_range_list = [];
    for item in period_range:
        # print (item);
        new_date = datetime.datetime.strptime(item, '%m/%d/%Y').strftime('%Y-%m-%d')
        # print (new_date);
        reformat_period_range_list.append(new_date);

    budget_list = budget_list[1:];

    # for item in budget_list:
    #     print (item);

    current_entity = '';

    budget_upload_list = [];

    for i in range(0, len(budget_list)):
        budget_item = budget_list[i];
        if current_entity == '':
            current_entity = budget_item[0];
        elif budget_item[0] != '' and current_entity != budget_item[0] :
            current_entity = budget_item[0];


        current_account = budget_item[1];
        current_account_name = budget_item[2];

        for period in reformat_period_range_list:
            index = reformat_period_range_list.index(period);
            value_index = index + 14;
            value = budget_item[value_index];
            budget_upload_item = ['',company_name, current_entity, data_date, current_account, current_account_name, period, value, budget_item[3],budget_item[4],budget_item[5],budget_item[6],budget_item[7],budget_item[8],budget_item[9],budget_item[10],budget_item[11],budget_item[12],budget_item[13]];
            budget_upload_list.append(budget_upload_item);

    # for item in budget_upload_list:
    #     print (item);

    # print (len(budget_upload_list));
    return budget_upload_list;



def read_respreads_input(file_path, company_name, data_date):
    with open(file_path, 'r') as f:
        reader = csv.reader(f);
        respread_list = list(reader);

    period_range = respread_list[0][14:];

    for item in period_range:
        print (item);


    reformat_period_range_list = [];
    for item in period_range:
        # print (item);
        new_date = datetime.datetime.strptime(item, '%m/%d/%Y').strftime('%Y-%m-%d')
        # print (new_date);
        reformat_period_range_list.append(new_date);

    respread_list = respread_list[1:];

    # for item in respread_list:
        # print (item);

    # sys.exit();

    current_entity = '';

    respread_upload_list = [];

    for i in range(0, len(respread_list)):
        respread_item = respread_list[i];
        if current_entity == '':
            current_entity = respread_item[0];
        elif respread_item[0] != '' and current_entity != respread_item[0] :
            current_entity = respread_item[0];


        current_account = respread_item[1];
        current_account_name = respread_item[2];
        current_model_group = respread_item[3];
        current_project_id = respread_item[4];
        current_project_name = respread_item[13];




        for period in reformat_period_range_list:
            index = reformat_period_range_list.index(period);
            value_index = index + 14;
            value = respread_item[value_index];
            respread_upload_item = ['',company_name, current_entity, data_date, current_account, current_account_name, period, value, current_model_group, current_project_id, current_project_name];
            respread_upload_item = respread_upload_item + respread_item[5:13];
            respread_upload_list.append(respread_upload_item);

    # for item in budget_upload_list:
    #     print (item);

    # print (len(budget_upload_list));
    return respread_upload_list;
