from utility import date_utils;
from database import db_configurator;
from database import db_controller;
from database import db_controller_labor;


from input import labor_uploader;

from logic import labor;

from display import disp_controller_labor;


import sys;

# BUDGET_SCENARIO = '2017 June AMR Budget';
# AMR_SCENARIO = '2017 June AMR';
# LAST_AMR_SCENARIO = '2017 May AMR';
# COMPANY = 'Lightstone';

""" dispatch back test settings """

def db_config_part():
    """
        step 1: we configre database connection
    """
    db_config_info = db_configurator.get_db_config_info();
    # print (db_config_info);
    host = db_config_info['host'];
    user = db_config_info['user'];
    password = db_config_info['password'];
    database = db_config_info['database'];

    conn_ins = db_controller.set_connection_instance_global(host, user, password, database);
    return conn_ins;


COMPANY = 'Lightstone';
SCENARIO = '2017 July AMR';


if __name__ == "__main__":
    print ("------------------Labor processing-------------------");

    conn_ins = db_config_part();

    # labor_uploader.labor_data_upload(conn_ins, COMPANY, SCENARIO);
    upload_to_financials_labor_expense_list, support_document_labor_expense_list = labor.process_labor(conn_ins, SCENARIO, COMPANY);

    db_controller.upload_cal_results_to_financials(conn_ins, upload_to_financials_labor_expense_list, COMPANY, SCENARIO);


    disp_controller_labor.labor_report(support_document_labor_expense_list, SCENARIO, COMPANY);
