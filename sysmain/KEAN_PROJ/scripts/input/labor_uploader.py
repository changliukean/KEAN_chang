import mysql.connector;
import pandas as pd;
import sys;
import datetime;
from pathlib import Path;
import os;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;



sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_labor;


LABOR_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/labor';




def labor_data_upload(conn_ins, company, scenario):
    print ("=================   uploading labor data to kean...");
    labor_file_input_folder = LABOR_FILE_INPUT_FOLDER;
    labor_input_file_list = os.listdir(labor_file_input_folder);
    for labor_file in labor_input_file_list:
        full_file_path = os.path.join(labor_file_input_folder, labor_file);
        if company in full_file_path and '~' not in full_file_path and 'labor' in labor_file:
            continue;
            print (full_file_path);
            labor_upload_list = read_labor_input(full_file_path, company, scenario);
            print (len(labor_upload_list));
            db_controller_labor.upload_labor_data(conn_ins, labor_upload_list, scenario, company);

        if company in full_file_path and '~' not in full_file_path and 'headcount' in labor_file:
            # print (full_file_path);
            headcount_upload_list = read_headcount_input(full_file_path, company, scenario);
            # print (len(budget_upload_list));
            db_controller_labor.upload_headcount_data(conn_ins, headcount_upload_list, scenario, company);


def read_labor_input(full_file_path, company, scenario):
    labor_data_df = pd.read_excel(full_file_path, header = 0);
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];
    # print (input_date);
    labor_upload_list = [];
    for item in labor_data_df:
        # print (len(labor_data_df[item]));
        if item == 'Plant Seniority Date':
            temp_list = list(labor_data_df[item]);
            temp_list = [datetime.datetime.strptime(str(item),"%m/%d/%Y").strftime("%Y-%m-%d") for item in temp_list];
            # print (temp_list);
            labor_upload_list.append(temp_list);
            continue;
        labor_upload_list.append(list(labor_data_df[item]));
    labor_upload_list = list(zip(*labor_upload_list));

    labor_upload_list = [ list((input_date, scenario, company) + item) for item in labor_upload_list];

    # print (len(labor_upload_list));

    # print (len(labor_upload_list[0]));

    return labor_upload_list;




def read_headcount_input(full_file_path, company, scenario):
    headcount_data_df = pd.read_excel(full_file_path, header=0);
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];

    temp_list = [];
    date_list = [];
    for item in headcount_data_df:

        if isinstance(item, datetime.datetime):
            # print (item);
            temp_list.append(list(headcount_data_df[item]));
            date_list.append(item);


    entity_list = [];
    for item in headcount_data_df:
        if item=='Entity':
            entity_list = list(headcount_data_df[item]);


    print (entity_list);

    # for item in temp_list:
    #     print (item);

    headcount_upload_list = [];
    for i in range(0, len(temp_list)):
        for j in range(0, len(temp_list[i])-1):
            headcount_upload_list.append([input_date, scenario, company, entity_list[j], str(date_list[i]).split(" ")[0], temp_list[i][j], temp_list[i][-1]]);

    # for item in headcount_upload_list:
    #     print (item);
    return headcount_upload_list;
