import pandas as pd;
import sys;
from pathlib import Path;
import datetime;
sys.path.insert(0, str(Path(__file__).parents[2])+r'/sysmain/KEAN_PROJ/scripts/utility');
import date_utils;



def upload_respreads(submit_file, company, scenario):
    respreads_upload_list = read_respreads_input(submit_file, company, scenario);
    return respreads_upload_list;



def read_respreads_input(full_file_path, company, scenario):
    respreads_data_df = pd.read_excel(full_file_path, header = 0);
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];
    respreads_upload_list = [];

    for item in respreads_data_df:
        if isinstance(item, datetime.datetime):
            if str(item).split(" ")[0] > input_date:
                for i in range(0, len(respreads_data_df)):
                    temp_info_list = list(respreads_data_df.iloc[i][['Plant','Account No','Account Title',\
                                           'Model group','Project ID','Cost Component ID','Work Order Number','Outage Code ID',\
                                           'Invoice ID', 'Contract Number ID','Reference number','Cost Category',\
                                           'Cost Sub Category','Project Name']])

                    for j in range(0, len(temp_info_list)):
                        if str(temp_info_list[j]) == 'nan':
                            temp_info_list[j] = '';

                    respreads_upload_list.append([company, scenario] + temp_info_list + [str(item).split(" ")[0],str(respreads_data_df[item].iloc[i]) if str(respreads_data_df[item].iloc[i]) != 'nan' else 0.0]);

    # for item in respreads_upload_list:
    #     print (item);

    return respreads_upload_list;
