
from utility import date_utils;
from database import db_configurator;
from database import db_controller;


from logic import hedge;
from display import disp_controller_hedge;


import sys;

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


    # print (str(conn_ins));
    scenario = '2017 July AMR';
    company = 'Lightstone';


    df_hedges, df_all_prices, df_hours_pjm = hedge.process_hedge(conn_ins, company, scenario, upload_to_kean=True);

    print (len(df_hedges));


    disp_controller_hedge.hedge_report(df_hedges, df_all_prices,df_hours_pjm, scenario, company);
