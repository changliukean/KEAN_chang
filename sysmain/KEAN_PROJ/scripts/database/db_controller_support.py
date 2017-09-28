"""
    db_controller.py file
    @module: db_utils
    @author: Andrew Good & Chang Liu
    @company: Kindle Energy
    @datetime: 2017-06-13
    @version: V1.0
    this file controls all operations related to database
    connection instance/create,update,insert,query,delete operations to the db
"""

import mysql.connector;
import pandas as pd;
import sys;
from sqlalchemy import *;

import db_configurator;
import db_controller;

# """ this is insane!!!!!!!!! """
# """ should use this one at the very beginning!!!!!!!!!!!!!!!!!!!! """
# engine = create_engine('mysql+mysqlconnector://Andrew:Kindle01@kindledb.cfdmlfy5ocmf.us-west-2.rds.amazonaws.com/kean')
# pxq_data_df.to_sql(name='pxq_input',con = engine, index=False, if_exists='append');


def upload_pxq_input(conn_ins, pxq_upload_list, scenario, company):

    db_config_info = db_configurator.get_db_config_info();
    engine_str = 'mysql+mysqlconnector://' + db_config_info['user'] +":" + db_config_info['password'] + "@" + db_config_info['host'] + "/" + db_config_info['database'];
    engine = create_engine(engine_str);
    pxq_upload_data_df = pd.DataFrame(data = pxq_upload_list, columns=['scenario','company','entity','data_source','input_title','period','value']);

    """ before we uploade, we want to clean the data related to same company and scenario """
    """ wipe out duplicates """
    delete_sql_str = "DELETE FROM pxq_input WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    pxq_upload_data_df.to_sql(name = 'pxq_input', con=engine, index=False, if_exists='append');



def get_pxq_input_data(conn_ins, scenario, company):
    query_sql_str = "SELECT * FROM pxq_input WHERE scenario = \'" + scenario + "\' AND company = \'" + company + "\';";
    pxq_input_data_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return pxq_input_data_df;

def get_budget_input_data_for_pxq(conn_ins, budget_scenario, company):
    pxq_account_name_list = ['On-Peak Generation','Off-Peak Generation','Total Generation', 'Realized On-Peak Power Price','Realized Off-Peak Power Price','Fossil Fuel Consumed','Delivered Fuel'];

    account_name_str = " in (";

    for item in pxq_account_name_list:
        account_name_str += "\'" +item+ "\' , ";

    account_name_str = account_name_str[:-2];

    account_name_str += ")";

    # print (account_name_str);

    query_sql_str = "SELECT * FROM budget WHERE scenario = \'" + budget_scenario + "\' AND company=\'" + company + "\' AND account_name " + account_name_str + ";";


    budget_data_for_pxq_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return budget_data_for_pxq_df;


def get_financials(conn_ins, company, scenario, version):
    query_sql_str = "SELECT * FROM financials WHERE company =\'" + company + "\' AND scenario = \'" + scenario + "\' AND version = \'" +version+ "\'";
    financials_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return financials_df;


def get_dispatch(conn_ins, company, scenario):
    query_sql_str = "SELECT * FROM dispatch WHERE company = \'" + company + "\' AND scenario = \'" +scenario+ "\'";
    dispatch_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return dispatch_df;
