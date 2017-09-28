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
from pathlib import Path;
import db_controller;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

def get_entity_plant_id(conn_ins, entity_name):
    # print (entity_name);
    query_sql_str = "SELECT plant_id FROM entity_name_mapping WHERE entity_name = \'" + entity_name +"\';";
    plant_id_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return plant_id_df.iloc[0]['plant_id'];

def get_tb_mapping_company(conn_ins, company_name, forecast_start_date, plant_id):
    query_sql_str =  "SELECT * FROM tb_mapping WHERE effective_end_date > \'" + str(forecast_start_date) + "\' AND lower(company) = lower(\'" + company_name + "\');";
    if plant_id:
        query_sql_str = "SELECT * FROM tb_mapping WHERE plant_id = \'" + plant_id + "\' AND effective_end_date > \'" + str(forecast_start_date) + "\' AND lower(company) = lower(\'" + company_name + "\');";
    # print (query_sql_str);
    tb_mapping_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return tb_mapping_df.groupby(['fsli']);

def get_tb_mapping(conn_ins, plant_id, data_date):
    query_sql_str = "SELECT * FROM tb_mapping WHERE plant_id = \'" + plant_id + "\' AND \'" + data_date + "\' >= effective_start_date AND \'" + data_date +  "\' <= effective_end_date;";
    tb_mapping_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return tb_mapping_df.groupby(['fsli']);


def update_forecast_budget_value(conn_ins, company, amr_scenario, budget_scenario, forecast_start_date):
    delete_sql_str = "delete from financials where company = \'" + company + "\' and scenario = \'" + amr_scenario + "\' and account in ('Maintenance','Operations','Removal Costs','Fuel Handling','Property Tax',\
												'Insurance', 'General & Administrative', 'Maintenance Capex',\
												'Environmental Capex','LTSA Capex','Growth Capex','EBITDA','EBITDA less Capex','Fixed Non-Labor Expense', 'Total Capex','Total Fixed Costs') and period > \'" + forecast_start_date + "\';";

    cursor = conn_ins.cursor(buffered=True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();


    insert_sql_str = "insert into financials (company, scenario, entity, account, period, value, version) select company, \'" + amr_scenario + "\', entity, account, period, value, '' from financials where account in\
                                            ('Maintenance','Operations','Removal Costs','Fuel Handling','Property Tax',\
											'Insurance', 'General & Administrative', 'Maintenance Capex',\
											'Environmental Capex','LTSA Capex','Growth Capex') and company = \'" + company + "\' and scenario = \'" + budget_scenario + "\' and version = 'vf' and period > \'" + forecast_start_date + "\';";
    cursor = conn_ins.cursor(buffered=True);
    cursor.execute(insert_sql_str);
    conn_ins.commit();
    return;


def upload_budget_data(conn_ins, budget_upload_list, scenario, company):
    print (len(budget_upload_list));
    """ clean up table for rows with same scenario name """
    delete_sql_str = "DELETE FROM budget WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();

    """ insert records """
    list_size = len(budget_upload_list);
    increment = 3000;
    remaining_size = list_size;
    start_index = 0;
    partition_list = [];
    while remaining_size > increment:
        remaining_size -= increment;
        partition_list.append((start_index, start_index+increment));
        start_index = start_index + increment;

    partition_list.append((start_index, start_index+remaining_size));

    for partition in partition_list:

        insert_sql_str = "INSERT INTO budget (company, scenario, entity, account, account_name, \
                          period, value, model_group, project_id, cost_component_id, work_order_number, \
                          outage_code_id, invoice_id, contract_number_id, reference_number, cost_category, \
                          cost_sub_category, project_name) VALUES ";

        """
            'Plant','Account No','Account Title','Model group','Project ID','Cost Component ID',\
                           'Work Order Number','Outage Code ID','Invoice ID','Contract Number ID',\
                           'Reference number','Cost Category','Cost Sub Category','Project Name',

        """

        for item in budget_upload_list[partition[0]:partition[1]]:

            item_company = str(item[15]);
            item_scenario = str(item[14]);
            item_entity = str(item[0]).strip();
            item_entity = item_entity if item_entity != 'HoldCO' else 'HoldCo';
            item_account = str(item[1]);
            item_account_name = str(item[2]).strip().replace("'",' ');

            item_period = str(item[16]);
            item_value = str(item[17]);


            item_model_group = str(item[3]);
            item_project_id = str(item[4]).strip();
            item_cost_component_id = str(item[5]);
            item_work_order_number = str(item[6]);
            item_outage_code_id = str(item[7]);
            item_invoice_id = str(item[8]);
            item_contract_number_id = str(item[9]);
            item_reference_number = str(item[10]);
            item_cost_catagory = str(item[11]);
            item_cost_sub_catagory = str(item[12]);
            item_project_name = str(item[13]);


            insert_item_list = [item_company,item_scenario,item_entity, item_account,\
            item_account_name, item_period, item_value, item_model_group,item_project_id,\
            item_cost_component_id,item_work_order_number,item_outage_code_id, item_invoice_id,\
            item_contract_number_id,item_reference_number,item_cost_catagory,\
            item_cost_sub_catagory,item_project_name];
            # print (insert_item_list);
            insert_sql_str += '( ';
            for insert_item in insert_item_list:
                """ be careful!!!!! we modified the raw data here!!!!!! """
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


def get_budget_data(conn_ins, company_name, scenario, period_range_list):
    period_range_str = date_utils.get_sql_where_clause_for_dates(period_range_list);

    query_sql_str = "SELECT * FROM budget WHERE company = \'" + company_name + "\' AND scenario = \'" + scenario + "\' AND period " + period_range_str + " ;";
    budget_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return budget_df;

def get_project_respreads_data(conn_ins, company_name, data_date, period_range_list):
    period_range_str = date_utils.get_sql_where_clause_for_dates(period_range_list);

    query_sql_str = "SELECT * FROM project_respread WHERE company = \'" + company_name + "\' AND data_date = \'" + data_date + "\' AND period " + period_range_str + " ;";
    budget_adjustment_df = db_controller.get_query_from_db(conn_ins, query_sql_str);
    return budget_adjustment_df;
