import mysql.connector;
import pandas as pd;
import sys;

import db_controller;
import datetime;

def get_all_libor(conn_ins, valuation_date, instrument_id):
    query = "SELECT period, rate FROM libor WHERE instrument_id = %s AND valuation_date = %s ";

    libor_df = pd.read_sql(query, conn_ins, params=[instrument_id, valuation_date]);

    return libor_df;


def get_all_swap(conn_ins, instrument_id):

    query = "SELECT date_start, date_end, notional, fixed_rate FROM swaps WHERE instrument_id = %s"

    df = pd.read_sql(query, conn_ins, params=[instrument_id])

    return df


def get_inception_debt_balance(conn_ins,instrument_id):
    ''' assumes only using 'Actuals' scenario, entity = 'HoldCo' and instrument_id has company '''

    cursor = conn_ins.cursor(buffered=True)

    query = ("SELECT amount FROM debt WHERE instrument_id = %s")

    try:
        cursor.execute(query, (instrument_id, ))
    except mysql.connector.Error as err:
        print(err.msg)

    record = cursor.fetchone()
    if record is not None:
        return record[0]
    else:
        return None


def get_inception_debt_date(conn_ins, instrument_id):
    ''' assumes only using 'Actuals' scenario, entity = 'HoldCo' and instrument_id has company '''

    cursor = conn_ins.cursor(buffered=True)
    query = ("SELECT inception_date FROM debt WHERE instrument_id = %s ")

    try:
        cursor.execute(query, (instrument_id, ))
    except mysql.connector.Error as err:
        print(err.msg)

    record = cursor.fetchone()
    if record is not None:
        return record[0]
    else:
        return None


def get_amort_percent(conn_ins, instrument_id):
    cursor = conn_ins.cursor(buffered=True)
    query = ("SELECT amortization FROM debt WHERE instrument_id = %s ")

    try:
        cursor.execute(query, (instrument_id, ))
    except mysql.connector.Error as err:
        print(err.msg)

    record = cursor.fetchone()
    if record is not None:
        return record[0]
    else:
        return None


def get_debt_activity_all(conn_ins, instrument_id):

    query = ("SELECT * FROM debt_payments WHERE instrument_id = %s")
    df = pd.read_sql(query, conn_ins, params=[instrument_id])

    return df


def get_cash(conn_ins, scenario):
    cursor = conn_ins.cursor(buffered=True)

    baml = '%%Bank of America%%'
    db = '%%Deutsche Lightstone%%'
    db_ex = 'Deutsche Lightstone Debt Srvc Reserve Acct SC5173.4'
    query = "SELECT accounting_month, sum(ending_balance) 'Cash EOP' FROM actuals WHERE scenario = \'" +scenario+ "\' AND " \
        " (account_title LIKE %s OR account_title LIKE %s) AND account_title <> %s " \
        "GROUP BY accounting_month ORDER BY accounting_month"
    df_tb = pd.read_sql(query, conn_ins, params=[baml, db, db_ex])
    df_tb.set_index('accounting_month', inplace=True)
    return df_tb


def get_actuals(conn_ins, account, column, column_title, scenario):
    query = "SELECT accounting_month, sum(" + column + ") '"+ column_title + "' FROM actuals WHERE scenario = \'" +scenario+ "\' AND account_title  = %s " \
        "GROUP BY accounting_month ORDER BY accounting_month"
    df_tb = pd.read_sql(query, conn_ins, params=[account])
    df_tb.set_index('accounting_month', inplace=True)
    return df_tb


def get_new_capex(conn_ins, scenario, entity, current_year, version=''):
    cursor = conn_ins.cursor(buffered=True)
    query = ("SELECT sum(value) FROM financials WHERE version = %s AND entity = %s AND scenario = %s "
            "AND account in ('Maintenance Capex', 'Environmental Capex', 'LTSA Capex', 'Growth Capex') "
            " AND period >= %s AND period <= %s")
    year_start = datetime.date(current_year, 1, 1)
    year_end = datetime.date(current_year, 12, 31)

    try:
        cursor.execute(query, (version, entity, scenario, year_start, year_end))
    except mysql.connector.Error as err:
        print(err.msg)

    record = cursor.fetchone()
    if record[0] is not None:
        return record[0]
    else:
        return 0


def build_ebitda(conn_ins, df_liquidity, scenario, company, version=''):
    query = ("SELECT period, SUM(value) EBITDA FROM financials WHERE version = %s AND company = %s "
            "AND account = 'EBITDA' AND scenario = %s GROUP BY company, period ORDER BY period")
    df = pd.read_sql(query, conn_ins, params=[version, company, scenario])
    df.set_index('period', inplace = True)
    df_add = df_liquidity.add(df, fill_value=0)
    return df_add


def build_capex(conn_ins, df_liquidity, scenario, company, version=''):
    query = ("SELECT period, SUM(value) Capex FROM financials WHERE version = %s AND company = %s "
            "AND scenario = %s AND account IN ('Maintenance Capex', 'Environmental Capex', 'LTSA Capex', 'Growth Capex') "
            "GROUP BY company, period ORDER BY period")
    df = pd.read_sql(query, conn_ins, params=[version, company, scenario])
    df.set_index('period', inplace = True)
    df_add = df_liquidity.add(df, fill_value=0)
    return df_add


def get_maintenance_capex(conn_ins, company, scenario, version):
    query_sql_str = "select sum(value), company, period from financials where scenario = \'" + scenario + "\' and version = \'" + version + "\' and account = 'Maintenance Capex' group by company, period;"
    maintenance_capex_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return maintenance_capex_df;


def get_ltsa_capex(conn_ins, company, scenario, version):
    query_sql_str = "select sum(value), company, period from financials where scenario = \'" + scenario + "\' and version = \'" + version + "\' and account = 'LTSA Capex' group by company, period;"
    maintenance_capex_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return maintenance_capex_df;
