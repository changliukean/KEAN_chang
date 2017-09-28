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

import db_controller;


def get_entity_plant_id(conn_ins, entity_name):
    query_sql_str = "SELECT plant_id FROM entity_name_mapping WHERE entity_name = \'" + entity_name +"\';";
    plant_id_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return plant_id_df.iloc[0]['plant_id'];

def get_entity_plant_id_holdco(conn_ins, entity_name):
    query_sql_str = "SELECT plant_id FROM entity_name_mapping WHERE entity_name = \'" + entity_name +"\';";
    plant_id_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return list(plant_id_df['plant_id']);

def get_tb_mapping_holdco(conn_ins, company_name, plant_id):

    plant_id_list_str = '(';

    for item in plant_id:
        plant_id_list_str += " \'" +str(item) + "\', ";

    plant_id_list_str = plant_id_list_str[:-2];
    plant_id_list_str += ')';


    query_sql_str = "SELECT * FROM tb_mapping WHERE plant_id in " + plant_id_list_str + " AND lower(company) = lower(\'" + company_name + "\') ;";
    # print (query_sql_str);
    tb_mapping_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return tb_mapping_df.groupby(['fsli']);


def get_tb_mapping(conn_ins, company_name, plant_id):
    query_sql_str = "SELECT * FROM tb_mapping WHERE plant_id = \'" + plant_id + "\' AND lower(company) = lower(\'" + company_name + "\');";
    # print (query_sql_str);
    tb_mapping_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return tb_mapping_df.groupby(['fsli']);


def get_actuals(conn_ins, company_name, scenario, entity_name=None):

    if not entity_name:
            query_sql_str = "SELECT * FROM actuals WHERE company = \'" + company_name + "\' AND scenario = \'" + scenario + "\' ;";
            # print (query_sql_str);
            actuals_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
            return actuals_df;

    query_sql_str = "SELECT * FROM actuals WHERE company = \'" + company_name + "\' AND entity = \'" + entity_name + "\' AND scenario = \'" + scenario + "\' ;";
    # print (query_sql_str);
    actuals_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return actuals_df;




def get_actuals_in_date_range(conn_ins, start_date, end_date):
    query_sql_str = "SELECT * FROM actuals WHERE accounting_month >= \'" + start_date +" \' AND accounting_month <= \'" + end_date + "\' ;";
    # print (query_sql_str);
    actuals_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return actuals_df;




def get_manual_inputs(conn_ins, company_name, entity_name, input_date):
    query_sql_str = "SELECT * FROM manual_inputs WHERE company = \'" + company_name + "\' AND entity = \'" + entity_name +"\' AND input_date = \'" + input_date + "\';"
    manual_inputs_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return manual_inputs_df;



def upload_actuals_data(conn_ins, actuals_upload_list, scenario, company):
    print (len(actuals_upload_list));
    """ clean up table for rows with same scenario name """
    delete_sql_str = "DELETE FROM actuals WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    """ insert records """
    list_size = len(actuals_upload_list);
    increment = 2000;
    remaining_size = list_size;
    start_index = 0;
    partition_list = [];
    while remaining_size > increment:
        remaining_size -= increment;
        partition_list.append((start_index, start_index+increment));
        start_index = start_index + increment;

    partition_list.append((start_index, start_index+remaining_size));

    for partition in partition_list:

        insert_sql_str = "INSERT INTO actuals (accounting_month, as_of_date, report_date, scenario, company,\
                          entity, plant_id, business_unit_id, account, account_title, bvr_group, project_id, project_name,\
                          period_balance, ending_balance, total_credit, total_debit, reference_number, contract_number,\
                          invoice_id, outage_code, work_order_number, cost_component) VALUES ";

        """
            'AS OF DATE','ACCOUNTING MONTH','BUSINESS UNIT ID','COMPANY NAME','BVR GROUP','ACCOUNT',\
                                                     'ACCOUNT TITLE','PROJECT ID', 'COST COMPONENT ID', 'WORK ORDER NUMBER', 'OUTAGE CODE ID',\
                                                     'INVOICE ID','CONTRACT NUMBER ID','REFERENCE NUMBER','PERIOD BALANCE', 'PLANT ID', 'REPORT_DATE',\
                                                     'ENDING BALANCE','TOTAL CREDIT','TOTAL DEBIT'
        """

        for item in actuals_upload_list[partition[0]:partition[1]]:
            as_of_date = str(item[0]);
            accounting_month = str(item[1]);
            report_date = str(item[16]);
            company = item[-1].strip();
            scenario = item[-2];

            business_unit_id = str(item[2]);
            entity = item[3];
            plant_id = item[15];
            plant_id = plant_id.strip();
            bvr_group = str(item[4]);
            account = item[5];
            account_title = item[6];
            account_title = account_title.replace("'",' ');
            project_id = str(item[7]);
            project_name = str(item[7]);
            cost_component = str(item[8]);
            work_order_number = str(item[9]);
            outage_code = str(item[10]);
            invoice_id = str(item[11]);
            contract_number = str(item[12]);
            reference_number = str(item[13]);
            period_balance = str(item[14]);
            ending_balance = str(item[17]);
            total_credit = str(item[18]);
            total_debit = str(item[19]);

            """
                accounting_month, as_of_date, report_date, scenario, company,\
                entity, plant_id, business_unit_id, account, account_title, bvr_group, project_id, project_name,\
                period_balance, ending_balance, total_credit, total_debit, reference_number, contract_number,\
                invoice_id, outage_code, work_order_number, cost_component
            """


            insert_item_list = [accounting_month, as_of_date, report_date, scenario, company, entity, plant_id, business_unit_id, \
                                            account, account_title, bvr_group, project_id, project_name,period_balance, \
                                            ending_balance, total_credit, total_debit, reference_number, contract_number, \
                                            invoice_id, outage_code, work_order_number, cost_component];
            # print (insert_item_list);
            insert_sql_str += '( ';
            for insert_item in insert_item_list:
                # print (insert_item);
                # print (type(insert_item));
                if insert_item == 'nan':
                    insert_item = '';
                insert_sql_str += "\'" + insert_item + "\', ";

            insert_sql_str = insert_sql_str[:-2];
            insert_sql_str += "),";

        insert_sql_str = insert_sql_str[:-1];
        insert_sql_str += ";";

        # print (insert_sql_str);
        print (partition);
        cursor = conn_ins.cursor(buffered=True);
        cursor.execute(insert_sql_str);
        conn_ins.commit();

    return 0;
