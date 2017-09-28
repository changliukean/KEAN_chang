import mysql.connector;
import pandas as pd;
import sys;

import db_controller;
from datetime import datetime;



def get_hedges(conn_ins, company, entity, date_start, date_end):

    date_start_str = datetime.strftime(date_start, '%Y-%m-%d')
    date_end_str = datetime.strftime(date_end, '%Y-%m-%d')

    query = "SELECT * FROM hedges WHERE company = \'" + company + \
            "\' AND entity = \'" + entity + "\' AND date_start <= \'" \
            + date_end_str + "\' AND date_end >= \'" + date_start_str + "\' " \
            + "ORDER BY date_start, tid_kindle"
    df_hedges = pd.read_sql(query, conn_ins)


    return df_hedges


def get_all_commodity_prices(conn_ins, scenario):

    # val_date_str = datetime.strftime(valuation_date, '%Y-%m-%d')

    query = "SELECT instrument_id, period, price FROM prices WHERE scenario = \'" + scenario + "\';";
    df_prices = pd.read_sql(query, conn_ins)

    return df_prices

def get_hours_pjm(conn_ins):
    query_sql_str = "SELECT * FROM hours_pjm";
    df_hours_pjm = pd.read_sql(query_sql_str, conn_ins);
    return df_hours_pjm;

def load_hedges_financials(conn_ins, scenario, company, entity, account, period, value):

    cursor = conn_ins.cursor()
    query = ("INSERT INTO financials(scenario, company, entity, account, period, value) "
            "VALUES(%s, %s, %s, %s, %s, %s)")
    try:
        cursor.execute(query, [scenario, company, entity, account, period, value])
    except mysql.connector.Error as err:
        print(err.msg)
    conn_ins.commit()
    cursor.close()
