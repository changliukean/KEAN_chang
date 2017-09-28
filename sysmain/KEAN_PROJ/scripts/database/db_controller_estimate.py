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



def get_query_from_db(conn_ins, query_sql_str):
    # print ('-----------------',CONNECTION_INSTANCE);
    result = pd.read_sql(query_sql_str, conn_ins);
    return result;



def get_dispatch_data(conn_ins, scenario, company):
    query_sql_str = "SELECT * FROM dispatch WHERE company = \'" + company + "\' AND scenario = \'" + scenario  + "\' ;"
    dispatch_df = get_query_from_db(conn_ins, query_sql_str);
    return dispatch_df;


def get_unit_counts_of_pp(conn_ins):
    query_sql_str = "select count(*), power_plant_name from poc_test_cl.power_plants group by power_plant_name;";
    unit_counts_df = get_query_from_db(conn_ins, query_sql_str);
    return unit_counts_df;


def get_financials_data_item(conn_ins, scenario, account):
    # print (period);
    query_sql_str = "SELECT * FROM financials WHERE scenario = \'" + scenario + "\' AND account = \'" + account + "\' ;";
    # print (query_sql_str);
    fin_data_item = get_query_from_db(conn_ins, query_sql_str);
    return fin_data_item;
