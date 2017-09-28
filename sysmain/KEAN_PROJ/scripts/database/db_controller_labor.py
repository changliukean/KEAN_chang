import mysql.connector;
import pandas as pd;
import sys;

import datetime;
from pathlib import Path;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller;

def upload_labor_data(conn_ins, labor_upload_list, scenario, company):
    delete_sql_str = "SET sql_safe_updates = 0;";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    delete_sql_str = "DELETE FROM labor_census where company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    upload_sql_str = "INSERT INTO labor_census (input_date, scenario, company, first_name, last_name, \
                      last_first_name, address, city, state, zip_code, default_job, \
                      employee_ein, employee_status, default_department, salary, plant_seniority_date, \
                      union_info, bonus_percentage, manager) VALUES "

    for item in labor_upload_list:
        temp_sql_str = "(";
        for item_sub in item:
            temp_sql_str += "\'" + str(item_sub) + "\', ";
        temp_sql_str = temp_sql_str[:-2];
        temp_sql_str += "), "
        upload_sql_str += temp_sql_str;

    upload_sql_str = upload_sql_str[:-2];


    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(upload_sql_str);
    conn_ins.commit();



def upload_headcount_data(conn_ins, headcount_upload_list, scenario, company):
    delete_sql_str = "SET sql_safe_updates = 0;";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    delete_sql_str = "DELETE FROM labor_headcount where company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    upload_sql_str = "INSERT INTO labor_headcount (input_date, scenario, company, entity, period,\
                    headcount,payroll_cycles) VALUES "

    for item in headcount_upload_list:
        temp_sql_str = "(";
        for item_sub in item:
            temp_sql_str += "\'" + str(item_sub) + "\', ";
        temp_sql_str = temp_sql_str[:-2];
        temp_sql_str += "), "
        upload_sql_str += temp_sql_str;

    upload_sql_str = upload_sql_str[:-2];


    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(upload_sql_str);
    conn_ins.commit();




def get_census(conn_ins, scenario, company):
    query_sql_str = "SELECT * FROM labor_census WHERE scenario = \'" + scenario + "\' AND company = \'" + company + "\';";
    census_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return census_df;


def get_headcount(conn_ins, scenario, company):
    query_sql_str = "SELECT * FROM labor_headcount WHERE scenario = \'" + scenario + "\' AND company = \'" + company + "\';";
    headcount_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return headcount_df;
