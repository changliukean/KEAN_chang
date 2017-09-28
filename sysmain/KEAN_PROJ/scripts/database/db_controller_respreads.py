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

import datetime;
import db_controller;


def upload_respreads_data(conn_ins, respread_upload_list,  company, scenario):
    delete_sql_str = "DELETE FROM project_respread where company = \'" +company+ "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor()
    cursor.execute(delete_sql_str)
    conn_ins.commit()

    print (len(respread_upload_list));

    insert_sql_str = "INSERT INTO project_respread (company, scenario, entity, account, account_name,  model_group,\
                                                    project_id,cost_component_id, work_order_number, outage_code_id,\
                                                    invoice_id, contract_number_id, reference_number, cost_category, cost_sub_category, project_name, period, value) VALUES ";

    for item in respread_upload_list:
        temp_sql_str = " ( \'" + company + "\', \'" + scenario + "\', "
        for item_s in item:
            # print (item_s);
            temp_sql_str += "\'" + str(item_s).strip() + "\', ";
        temp_sql_str = temp_sql_str[:-2];
        temp_sql_str += "), ";
        insert_sql_str += temp_sql_str;

    insert_sql_str = insert_sql_str[:-2];

    # print (insert_sql_str);
    # sys.exit();
    cursor = conn_ins.cursor()
    cursor.execute(insert_sql_str);
    conn_ins.commit();

    return 0;

def get_respreads(conn_ins, company, scenario):
    query_sql_str = "SELECT * FROM project_respread WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    respreads_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return respreads_df;
