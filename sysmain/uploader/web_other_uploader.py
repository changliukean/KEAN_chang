import pandas as pd;
import sys;
from pathlib import Path;
import datetime;
sys.path.insert(0, str(Path(__file__).parents[2])+r'/sysmain/KEAN_PROJ/scripts/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[2])+r'/sysmain/KEAN_PROJ/scripts/database');
import db_controller;
import db_controller_labor;






from django.db import connection;




def db_config_part(django_connection_dict):
    """
        step 1: we configre database connection
    """

    host = django_connection_dict['HOST'];
    user = django_connection_dict['USER'];
    password = django_connection_dict['PASSWORD'];
    database = django_connection_dict['NAME'];

    conn_ins = db_controller.set_connection_instance_global(host, user, password, database);
    return conn_ins;


def support_pxq_data_upload(submit_file_path, company, scenario):
    print ("=================   uploading pxq data to kean...");
    conn_ins = db_config_part(connection.settings_dict);
    pxq_upload_list = pxq_data_upload(conn_ins, submit_file_path, company, scenario);
    return pxq_upload_list;

def pxq_data_upload(conn_ins, submit_file_path, company, scenario):
    pxq_upload_list = read_pxq_input(conn_ins, submit_file_path, company, scenario);
    return pxq_upload_list;




def read_pxq_input(conn_ins, pxq_input_file_path, company_name, amr_scenario):
    pxq_upload_list = [];
    pxq_data_df = pd.read_excel(pxq_input_file_path,header = 0);

    date_range_list = [];

    for item in pxq_data_df:
        # print (item);
        if '-' in str(item):
            date_range_list.append(item);

    print ("----------------------------------");


    pxq_info_list = [];

    for item in pxq_data_df:
        if item in ['Entity','Category','Title']:
            pxq_info_list.append(list(pxq_data_df[item]));


    for item in date_range_list:
        period = item;
        value_list = list(pxq_data_df[item]);

        for i in range(0, len(value_list)):
            try:
                value_list[i] = float(str(value_list[i]));
            except:
                value_list[i] = 0.0;

            if str(value_list[i]) == 'nan':
                value_list[i] = 0.0;

            value_list[i] = str(value_list[i]);


        period_list = [str(period).split(" ")[0] for i in range(len(value_list))];
        company_list = [company_name for i in range(len(value_list))];
        scenario_list = [amr_scenario for i in range(len(value_list))];
        temp_upload_list = [scenario_list] + [company_list] + pxq_info_list + [period_list] + [value_list];
        # for t_list in temp_upload_list:
        #     print (len(t_list));
        # break;
        pxq_upload_list = pxq_upload_list + list(zip(*temp_upload_list));



    return pxq_upload_list;








def manual_data_upload(submit_file_path, company, scenario, version = ''):
    print ("=================   uploading manual data to kean...");
    conn_ins = db_config_part(connection.settings_dict);
    respreads_upload_list = read_manual_input(submit_file_path, company, scenario);
    db_controller.upload_cal_results_to_financials(conn_ins, respreads_upload_list, company, scenario, version);

def read_manual_input(full_file_path, company, scenario):
    respreads_data_df = pd.read_excel(full_file_path, header = 0);
    print (len(respreads_data_df));
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];
    respreads_upload_list = [];
    """
        account
    """

    print (input_date);

    for item in respreads_data_df:
        if isinstance(item, datetime.datetime):
            if str(item).split(" ")[0] > input_date:
                # print (item);
                # value_list.append(list(respreads_data_df[item]));
                for i in range(0, len(respreads_data_df)):
                    respreads_upload_list.append([company] + [list(respreads_data_df.iloc[i][['Entity','FSLI']])[0]] + [scenario] + [list(respreads_data_df.iloc[i][['Entity','FSLI']])[1]] + [str(item).split(" ")[0],str(respreads_data_df[item].iloc[i])]);

    for item in respreads_upload_list:
        print (item);

    print (len(respreads_upload_list));

    return respreads_upload_list;


def labor_data_upload(submit_file_path, company, scenario):
    print ("=================   uploading labor data to kean...");
    conn_ins = db_config_part(connection.settings_dict);

    labor_upload_list = read_labor_input(submit_file_path, company, scenario);
    db_controller_labor.upload_labor_data(conn_ins, labor_upload_list, scenario, company);

    headcount_upload_list = read_headcount_input(submit_file_path, company, scenario);
    db_controller_labor.upload_headcount_data(conn_ins, headcount_upload_list, scenario, company);


def read_labor_input(full_file_path, company, scenario):
    labor_data_df = pd.read_excel(full_file_path, 'labor' ,header = 0);
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


    return labor_upload_list;




def read_headcount_input(full_file_path, company, scenario):
    headcount_data_df = pd.read_excel(full_file_path, 'headcount' ,header=0);
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



    headcount_upload_list = [];
    for i in range(0, len(temp_list)):
        for j in range(0, len(temp_list[i])-1):
            headcount_upload_list.append([input_date, scenario, company, entity_list[j], str(date_list[i]).split(" ")[0], temp_list[i][j], temp_list[i][-1]]);


    return headcount_upload_list;
