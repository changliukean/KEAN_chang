import csv;
import datetime;
import sys;
import os;
from pathlib import Path;
import pandas as pd;





sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller;
import db_controller_support;


PXQ_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/support_docs';


def pxq_data_upload(conn_ins, company, amr_scenario):
    print ("=================   uploading p x q data to kean...");
    pxq_file_input_folder = PXQ_FILE_INPUT_FOLDER;
    pxq_input_file_list = os.listdir(pxq_file_input_folder);
    for pxq_file in pxq_input_file_list:
        full_file_path = os.path.join(pxq_file_input_folder, pxq_file);
        # print (full_file_path);
        if company in full_file_path and '~' not in full_file_path and 'pxq' in full_file_path:
            print (full_file_path);
            pxq_upload_list = read_pxq_input(conn_ins, full_file_path, company, amr_scenario);
            print (len(pxq_upload_list));
            db_controller_support.upload_pxq_input(conn_ins, pxq_upload_list, amr_scenario, company);


    return 0;




def read_pxq_input(conn_ins, pxq_input_file_path, company_name, amr_scenario):
    pxq_upload_list = [];
    pxq_data_df = pd.read_excel(pxq_input_file_path,header = 0);

    date_range_list = [];

    for item in pxq_data_df:
        # print (item);
        if '-' in str(item):
            date_range_list.append(item);

    print ("----------------------------------");
    # for item in date_range_list:
    #     print (item);


    pxq_info_list = [];

    for item in pxq_data_df:
        # print (item);
        if item in ['Entity','Category','Title']:
            pxq_info_list.append(list(pxq_data_df[item]));

    # for item in pxq_info_list:
    #     print (len(item));

    # pxq_info_list = list(zip(*pxq_info_list));

    # for item in pxq_info_list:
    #     print (item);

    for item in date_range_list:
        period = item;
        value_list = list(pxq_data_df[item])
        period_list = [period for i in range(len(value_list))];
        company_list = [company_name for i in range(len(value_list))];
        scenario_list = [amr_scenario for i in range(len(value_list))];
        temp_upload_list = [scenario_list] + [company_list] + pxq_info_list + [period_list] + [value_list];
        # for t_list in temp_upload_list:
        #     print (len(t_list));
        # break;
        pxq_upload_list = pxq_upload_list + list(zip(*temp_upload_list));


    return pxq_upload_list;
