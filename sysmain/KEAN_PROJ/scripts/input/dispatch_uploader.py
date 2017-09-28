import mysql.connector;
import pandas as pd;
import sys;
import datetime;
from pathlib import Path;
import os;

DISPATCH_FILE_INPUT_FOLDER = str(Path(__file__).parents[2]) + r'/data/dispatch';
SHEET_NAME_DICT = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby']};






def read_dispatch_data_from_xlsx(xlsx_file_path, tab_name, scenario, company):
    dispatch_df = pd.read_excel(xlsx_file_path, tab_name, header=None);



    # print ("===================");
    # print (dispatch_df);
    # print ("===================");
    result_list = [];
    for i in range(1, len(dispatch_df)):
        for j in range(1, len(dispatch_df.iloc[i])):
            # print (dispatch_df.iloc[i][0]);
            result_list.append([scenario, tab_name, dispatch_df.iloc[i][0], str(dispatch_df.iloc[0][j]).split(" ")[0], dispatch_df.iloc[i][j], company]);


    return result_list;


def upload_dispatch(conn_ins, dispatch_list, scenario, company):
    """ delete data with same scenario name """
    delete_sql_str = "DELETE FROM dispatch WHERE scenario = \'" + scenario + "\' AND company = \'" + str(company) + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();



    insert_sql_str = "INSERT INTO dispatch (scenario, entity, fsli, period, value, company) VALUES ";

    for item in dispatch_list:
        insert_sql_str += "(";
        for item_i in item:
            insert_sql_str += "\'" + str(item_i) + "\', ";
        insert_sql_str = insert_sql_str[:-2];
        insert_sql_str += "), ";

    insert_sql_str = insert_sql_str[:-2];
    insert_sql_str += ";";

    cursor = conn_ins.cursor(buffered=True);
    cursor.execute(insert_sql_str);
    conn_ins.commit();
    return 0;




def dispatch_data_upload(conn_ins, company, scenario):

    dispatch_file_input_folder = DISPATCH_FILE_INPUT_FOLDER;
    dispatch_input_file_list = os.listdir(dispatch_file_input_folder);
    dispatch_file_path = '';
    for dispatch_file in dispatch_input_file_list:
        full_file_path = os.path.join(dispatch_file_input_folder, dispatch_file);
        if company in full_file_path and '~' not in full_file_path and scenario in full_file_path:
            dispatch_file_path = full_file_path;

    tab_name_list = SHEET_NAME_DICT[company];


    dispatch_list = [];
    for tab_name in tab_name_list:
        try:
            result_list = read_dispatch_data_from_xlsx(dispatch_file_path, tab_name, scenario, company);
            dispatch_list += result_list;
        except:
            print('No tab name found for ',tab_name);

    print (len(dispatch_list));
    # sys.exit();

    upload_dispatch(conn_ins, dispatch_list, scenario, company);
