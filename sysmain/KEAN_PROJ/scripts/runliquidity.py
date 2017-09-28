

from utility import date_utils;
from database import db_configurator;
from database import db_controller;


from logic import liquidity;
from display import disp_controller_liquidity;


import sys;



AMR_SCENARIO = '2017 July AMR';
COMPANY = 'Lightstone';


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

    # db_controller.set_connection_instance_global(host,user,password,database);

    conn_ins = db_controller.set_connection_instance_global(host, user, password, database);
    return conn_ins;



if __name__ == '__main__':
    print ("------------------Liquidity processing-------------------");
    """
        step 1: config db connection
    """
    conn_ins = db_config_part();


    # print (conn_ins);


    df_liquidity, tax_depreciation_result = liquidity.process_liquidity(conn_ins);


    print (" start to generate report ");
    print (len(tax_depreciation_result));

    import pandas as pd;
    # df_liquidity = pd.DataFrame.from_csv('liquidity backup_20.csv');
    disp_controller_liquidity.liquidity_report(df_liquidity, AMR_SCENARIO, COMPANY);
    disp_controller_liquidity.debt_balance_report(df_liquidity, AMR_SCENARIO, COMPANY);
    disp_controller_liquidity.interest_expense_report(df_liquidity, AMR_SCENARIO, COMPANY);
    disp_controller_liquidity.est_tax_dist_report(df_liquidity, tax_depreciation_result, AMR_SCENARIO, COMPANY);
