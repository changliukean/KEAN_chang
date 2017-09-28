import mysql.connector;
import pandas as pd;
import sys;
import datetime;
from pathlib import Path;
import os;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;



sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_respreads;


RESPREADS_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/respreads';




def respreads_data_upload(conn_ins, company, scenario):
    print ("=================   uploading labor data to kean...");
    respreads_file_input_folder = RESPREADS_FILE_INPUT_FOLDER;
    respreads_input_file_list = os.listdir(respreads_file_input_folder);
    for respreads_file in respreads_input_file_list:
        full_file_path = os.path.join(respreads_file_input_folder, respreads_file);
        if company in full_file_path and '~' not in full_file_path and 'respreads' in respreads_file and scenario in respreads_file:
            print (full_file_path);
            respreads_upload_list = read_respreads_input(full_file_path, company, scenario);
            db_controller_respreads.upload_respreads_data(conn_ins, respreads_upload_list, company, scenario);


def read_respreads_input(full_file_path, company, scenario):
    respreads_data_df = pd.read_excel(full_file_path, header = 0);
    print (len(respreads_data_df));
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];
    respreads_upload_list = [];
    """
        Plant	Account No	Account Title	Model group	Project ID	Cost Component ID	Work Order Number	Outage Code ID	Invoice ID	Contract Number ID	Reference number	Cost Category	Cost Sub Category	Project Name
    """

    print (input_date);

    for item in respreads_data_df:
        if isinstance(item, datetime.datetime):
            if str(item).split(" ")[0] > input_date:
                # print (item);
                # value_list.append(list(respreads_data_df[item]));
                for i in range(0, len(respreads_data_df)):
                    respreads_upload_list.append(list(respreads_data_df.iloc[i][['Plant','Account No','Account Title',\
                    	                                       'Model group','Project ID','Cost Component ID','Work Order Number','Outage Code ID',\
                                                               'Invoice ID', 'Contract Number ID','Reference number','Cost Category',\
                                                               'Cost Sub Category','Project Name']]) + [str(item).split(" ")[0],str(respreads_data_df[item].iloc[i])]);

    # for item in respreads_upload_list:
    #     print (item);
    #
    return respreads_upload_list;
