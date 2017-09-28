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

AMR_SIGNS_DICT = {'Energy Revenue':1.0, 'Delivered Fuel Expense':-1.0,'Net Emissions Expense':-1.0,\
                  'Variable O&M Expense':-1.0, 'Fixed Fuel':-1.0, 'Gross Energy Margin':1.0,\
                  'Hedge P&L':1.0, 'Net Energy Margin':1.0,'Capacity Revenue':1.0,\
                  'Ancillary Services Revenue':1.0,'Misc Income':1.0,'Total Other Income':1.0,\
                  'Gross Margin':1.0,'Labor Expenses':-1.0,'Maintenance':-1.0,'Operations':-1.0,\
                  'Removal Costs':-1.0,'Fuel Handling':-1.0,'Fixed Non-Labor Expense':1.0,\
                  'Property Tax':-1.0,'Insurance':-1.0,'General & Administrative':-1.0,\
                  'Total Fixed Costs':1.0,'EBITDA':1.0,'Maintenance Capex':-1.0,\
                  'Environmental Capex':-1.0,'LTSA Capex':-1.0,'Growth Capex':-1.0,\
                  'Total Capex':-1.0,'EBITDA less Capex':1.0}


"""
    this global connection instance is used by all db methods
"""
CONNECTION_INSTANCE = 0;


"""
    method generate_connection_instance
    given the host, user, password, database, this method will generate a mysql.connector instance
    then we use this instance for all sql operations by passing it as a parameter
"""
def set_connection_instance_global(host, user, password, database):
    global CONNECTION_INSTANCE;
    CONNECTION_INSTANCE = mysql.connector.connect(host = host,user = user, password = password, database = database);
    return CONNECTION_INSTANCE;

def get_query_from_db(conn_ins, query_sql_str):
    # print ('-----------------',CONNECTION_INSTANCE);
    result = pd.read_sql(query_sql_str, conn_ins);
    return result;


def get_format_list_by_template_name(conn_ins,template_name):
    query_sql_str = "select pt.id_template, pt.template_name, pt.author, pft.id_format, pf.format_name, pf.format_dict_string \
    from template pt join format_template pft on pt.id_template = pft.id_template\
    join format pf on pft.id_format = pf.id_format where pt.template_name = \'" + template_name + "\' ";
    # print (query_sql_str);
    # sys.exit();
    format_result = get_query_from_db(conn_ins,query_sql_str);
    # print (format_result.iloc[0]['format_dict_string']);
    return format_result;


def get_query_df_by_where_clause(conn_ins, table_name, select_columns, where_clause):
    select_columns_str = ', '.join(select_columns) if len(select_columns) > 1 else select_columns[0];
    query_sql_str = "SELECT " + select_columns_str + " FROM " + table_name + " " + where_clause + ";";
    # print ("=======================");
    # print (query_sql_str);
    # print ("=======================");
    result_df = pd.read_sql(query_sql_str, conn_ins);
    return result_df;



"""
    method get_csv_dataframe_from_relativepath
    given the relative_path of a csv file, we read in the file and store the data in a pandas dataframe
"""
def get_csv_dataframe_from_relativepath(relative_path):
    csv_df = pd.DataFrame.from_csv(relative_path, sep=';', header = 0);
    return csv_df;


"""
    method insert_into_aws_db_from_pddf
    given a pandas dataframe, we insert all data into a AWS mysql server table
    this method is using pure sql statement, not very sufficent when the number of records reach millions
    and might be rejected by the server when the length of the sql statement string is greater than the limit
"""
def insert_into_aws_db_from_pddf(conn_ins,table_name,pddf):

    insert_sql_str = "INSERT INTO " + table_name + " VALUES ";

    for i in range(0, len(pddf)):
        insert_sql_str += " ( " + str(i+1) + ' , ' + ' , '.join(["\'" + str(subitem) + "\'" for subitem in list((pddf.iloc[0]))]) + " ),";

    # print (len(insert_sql_str));
    insert_sql_str = insert_sql_str[:-1];
    insert_sql_str += ";";
    # print (len(insert_sql_str));
    # sys.exit();
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(insert_sql_str);
    conn_ins.commit();
    return 0;


def get_results_from_financials(conn_ins, company_name, scenario, entity_name = None, data_date=None, data_start_date=None, data_end_date=None, version=''):
    query_sql_str = "SELECT * FROM financials WHERE company = \'" + company_name + "\' AND scenario = \'" + scenario + "\' AND version = \'" + version + "\'";
    if entity_name != None:
        query_sql_str = "SELECT * FROM financials WHERE company = \'" + company_name +"\' AND entity = \'" + entity_name + "\' AND scenario = \'" + scenario + "\'" + " AND version = \'" + version + "\';";

    if data_date != None:
        query_sql_str = "SELECT * FROM financials WHERE company = \'" + company_name +"\' AND scenario = \'" + scenario + "\' AND data_date = \'" + str(data_date) +"\' AND version = \'" + version + "\';";

    if data_start_date != None and data_end_date != None:
        query_sql_str = "SELECT * FROM financials WHERE company = \'" + company_name +"\' AND scenario = \'" + scenario + "\' AND period >= \'" + str(data_start_date) +"\' AND period <= \'" + str(data_end_date) + "\' AND version = \'" + version +"\';";
        # print (query_sql_str);



    financials_result_df = get_query_from_db(conn_ins, query_sql_str);
    # print (query_sql_str);
    return financials_result_df;


def get_fixed_cells(conn_ins, template_name, tab_name):
    query_sql_str = "select * from template pt join tab_fixed_cells ptfc \
                    on pt.id_template = ptfc.id_template join format pf \
                    on ptfc.id_format = pf.id_format WHERE template_name = \'" + template_name + "\' AND ptfc.tab_name = \'" + tab_name +"\' ;";

    # print (query_sql_str);
    fixed_cells_df = get_query_from_db(conn_ins, query_sql_str);
    return fixed_cells_df;

def get_adjustment_for_tab(conn_ins, template_name, tab_name):
    query_sql_str = "select * from template pt join tab_adjustment pta \
                    on pt.id_template = pta.id_template WHERE template_name = \'" + template_name + "\' AND pta.tab_name = \'" + tab_name +"\'  ;";
    report_adjustment_df = get_query_from_db(conn_ins, query_sql_str);
    return report_adjustment_df;



def get_adjustment_financials(conn_ins,scenario, company):
    query_sql_str = "SELECT * FROM adjustment_financials WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    adjustment_financials_df = get_query_from_db(conn_ins, query_sql_str);
    return adjustment_financials_df;

def update_financials_adjustment_without_calcs(conn_ins, scenario, company):
    update_sql_str = "SET SQL_SAFE_UPDATES = 0";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(update_sql_str);
    conn_ins.commit();


    query_sql_str = "SELECT * FROM financials_adjustment WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\' ;";
    adjustment_financials_df = get_query_from_db(conn_ins, query_sql_str);
    for i in range(0, len(adjustment_financials_df)):
        current_company = adjustment_financials_df.iloc[i]['company'];
        current_entity = adjustment_financials_df.iloc[i]['entity'];
        current_scenario = adjustment_financials_df.iloc[i]['scenario'];
        current_account = adjustment_financials_df.iloc[i]['account'];
        current_period = adjustment_financials_df.iloc[i]['period'];
        adjustment = adjustment_financials_df.iloc[i]['adjustment'];

        print ("-------------------------------------------------");
        print ("warning ! we modified: " + current_entity, current_scenario, current_account, current_period);
        print ("-------------------------------------------------");

        update_sql_str = "UPDATE financials SET value = value + " + str(adjustment) + " WHERE company = \'" + current_company + "\' AND ";
        update_sql_str += " entity = \'" + current_entity + "\' AND ";
        update_sql_str += " scenario = \'" + current_scenario + "\' AND ";
        update_sql_str += " account = \'" + current_account + "\' AND ";
        update_sql_str += " period = \'" + str(current_period) + "\' AND ";
        update_sql_str += " version = \'\' ;";

        """
            We only adjust the values for financials when there are no version info specified
            if there is a scenario in the financials table with no version info,
            that means we are still working on the generating the values,
            we haven't achieved a VERSION

            the reason for designing in this way is we don't want to many versions in kean system
            for each AMR, the results are coming from different place, it's hard to make a consistent version number for all those numbers
            we only do version info update when we have a complete set of results uploaded to kean

            if there is a version info for a row in financials, that means it's already adjusted
        """

        cursor = conn_ins.cursor(buffered = True);
        cursor.execute(update_sql_str);
        conn_ins.commit();

    return 0;


# def upload_cal_results_to_financials_multi_scenario(conn_ins, result_value_list_dict):
#     for scenario in result_value_list_dict:
#         upload_cal_results_to_financials(conn_ins, result_value_list_dict[scenario], scenario);
#
#


def get_company_entity_info_by_company_name(conn_ins, company_name):
    query_sql_str = "SELECT * FROM company_entity WHERE company_name = \'" + company_name + "\' ;"
    company_entity_df = get_query_from_db(conn_ins, query_sql_str);
    return company_entity_df;


def get_entity_info(conn_ins, entity_name):
    query_sql_str = "SELECT * FROM power_plants WHERE power_plant_name = \'" + entity_name + "\' ;"
    entity_info_df = get_query_from_db(conn_ins, query_sql_str);
    return entity_info_df;


def update_financials_calcs(conn_ins, scenario, company_name, date_list, version = ''):
    print ('heyhey');

    date_list_str = "(";
    for a_date in date_list:
        date_list_str += "\'" + str(a_date) + "\', ";

    date_list_str = date_list_str[:-2] + ")";


    query_sql_str = "SELECT * FROM financials WHERE scenario = \'" + scenario + "\' AND company = \'" + company_name + "\' AND version = \'" + version + "\' AND period in " + date_list_str + ";";

    # print (query_sql_str);

    financials_result_df = get_query_from_db(conn_ins, query_sql_str);

    if len(financials_result_df) == 0:
        print ("------------------ warning ------------------");
        print ("Financials data not found for scenario: ",scenario, " version: ", version if version!='' else '(Blank)' );
        print ("Try changing scenario name or version info. ");
        print ("---------------------------------------------");
        return 0;


    calc_account_dict = {'Gross Energy Margin':[['Energy Revenue',1],['Delivered Fuel Expense',-1],['Net Emissions Expense',-1],['Variable O&M Expense',-1],['Fixed Fuel',-1]],\
                         'Net Energy Margin':[['Energy Revenue',1],['Delivered Fuel Expense',-1],['Net Emissions Expense',-1],['Variable O&M Expense',-1],['Fixed Fuel',-1],['Hedge P&L',1]],\
                         'Total Other Income':[['Capacity Revenue',1],['Ancillary Services Revenue',1],['Misc Income',1]],\
                         'Gross Margin':[['Energy Revenue',1],['Delivered Fuel Expense',-1],['Net Emissions Expense',-1],['Variable O&M Expense',-1],['Fixed Fuel',-1],['Hedge P&L',1],['Capacity Revenue',1],['Ancillary Services Revenue',1],['Misc Income',1]],\
                         'Fixed Non-Labor Expense':[['Maintenance',1],['Operations',1],['Removal Costs',1],['Fuel Handling',1]],\
                         'Total Fixed Costs':[['Labor Expenses',1],['Maintenance',1],['Operations',1],['Removal Costs',1],['Fuel Handling',1], ['Property Tax',1],['Insurance',1],['General & Administrative',1]],\
                         'EBITDA':[['Energy Revenue',1],['Delivered Fuel Expense',-1],['Net Emissions Expense',-1],['Variable O&M Expense',-1],['Fixed Fuel',-1],['Hedge P&L',1],['Capacity Revenue',1],['Ancillary Services Revenue',1],['Misc Income',1], ['Labor Expenses',-1],['Maintenance',-1],\
                                    ['Operations',-1],['Removal Costs',-1],['Fuel Handling',-1], ['Property Tax',-1],['Insurance',-1],['General & Administrative',-1]],\
                         'Total Capex':[['Maintenance Capex',1],['Environmental Capex',1],['LTSA Capex',1],['Growth Capex',1]],\
                         'EBITDA less Capex':[['Energy Revenue',1],['Delivered Fuel Expense',-1],['Net Emissions Expense',-1],['Variable O&M Expense',-1],['Fixed Fuel',-1],['Hedge P&L',1],['Capacity Revenue',1],['Ancillary Services Revenue',1],['Misc Income',1], ['Labor Expenses',-1],['Maintenance',-1],\
                                                ['Operations',-1],['Removal Costs',-1],['Fuel Handling',-1], ['Property Tax',-1],['Insurance',-1],['General & Administrative',-1],['Maintenance Capex',-1],['Environmental Capex',-1],['LTSA Capex',-1],['Growth Capex',-1]]};

    calc_financials_result_df = financials_result_df.loc[financials_result_df['account'].isin(calc_account_dict)];

    entity_list = list(set(list(financials_result_df['entity'])));

    calc_modify_list = [];
    for entity_item in entity_list:
        for date_item in date_list:
            date_obj = datetime.datetime.strptime(date_item,"%Y-%m-%d").date();
            for calc_account in calc_account_dict:

                calc_modify_list.append([scenario, company_name, entity_item, calc_account ,date_obj]);



    upload_to_financials_list = [];



    # print (len(calc_modify_list));

    for pair in calc_modify_list:
        current_scenario = pair[0];
        current_company = pair[1];
        current_entity = pair[2];
        current_account = pair[3];
        current_period = pair[4];



        new_value = 0.0;


        calc_items_list = calc_account_dict[current_account];
        calc_account_list = list(zip(*calc_items_list))[0];

        temp_financials_result_df = financials_result_df.loc[(financials_result_df['scenario'] == current_scenario) &\
                                                 (financials_result_df['company'] == current_company) &\
                                                 (financials_result_df['entity'] == current_entity) &\
                                                 (financials_result_df['account'].isin(calc_account_list)) &\
                                                 (financials_result_df['period'] == current_period)];

        # print (temp_financials_result_list);

        temp_account_value_list = list(zip(temp_financials_result_df.account,temp_financials_result_df.value));
        # print (temp_account_value_list);

        if len(temp_account_value_list) > 0:
            for i in range(0, len(temp_account_value_list)):
                sign = [item[1] for item in calc_items_list if item[0] == temp_account_value_list[i][0]][0];
                new_value += sign * temp_account_value_list[i][1];


        # print (len(temp_financials_result_df));
        #
        #
        #
        #
        # for item in calc_account_dict[current_account]:
        #     if len(temp_financials_result_df.loc[(temp_financials_result_df['scenario'] == current_scenario) &\
        #                                          (temp_financials_result_df['company'] == current_company) &\
        #                                          (temp_financials_result_df['entity'] == current_entity) &\
        #                                          (temp_financials_result_df['account'] == item[0] ) &\
        #                                          (temp_financials_result_df['period'] == current_period)]['value']) == 1:
        #         new_value += item[1] * temp_financials_result_df.loc[(temp_financials_result_df['scenario'] == current_scenario) &\
        #                                              (temp_financials_result_df['company'] == current_company) &\
        #                                              (temp_financials_result_df['entity'] == current_entity) &\
        #                                              (temp_financials_result_df['account'] == item[0] ) &\
        #                                              (temp_financials_result_df['period'] == current_period)]['value'].iloc[0];


        # new_value = sum(list([item[1] * .iloc[0] for item in calc_account_dict[current_account]]));

        upload_to_financials_list.append([current_company, current_entity, current_scenario, current_account, current_period, new_value]);

    # for item in upload_to_financials_list:
    #     print (item);

    # print ("SEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", scenario);
    upload_cal_results_to_financials(conn_ins,upload_to_financials_list, company_name, scenario, version);

def get_lc_facilities_letters_of_credit(conn_ins, company_name):
    query_sql_str = "SELECT * FROM lc_facilities WHERE company = \'" +company_name+ "\'";
    lc_facilities_df = get_query_from_db(conn_ins, query_sql_str);
    query_sql_str = "SELECT * FROM letters_of_credit WHERE company = \'" + company_name + "\'";
    letters_of_credit_df = get_query_from_db(conn_ins, query_sql_str);
    return lc_facilities_df, letters_of_credit_df;



def update_version_info_financials(conn_ins, company, scenario, version):
    update_sql_str = "SET SQL_SAFE_UPDATES = 0";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(update_sql_str);
    conn_ins.commit();


    delete_sql_str = "DELETE FROM financials WHERE company = \'" + company + "\' and scenario = \'" + scenario + "\' and version = \'" + version + "\'";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(delete_sql_str);
    conn_ins.commit();


    update_sql_str = "insert into financials (company, entity, scenario, account, period, value, version) select company, entity, scenario, account, period, value, \'" + version + "\' from financials where company = \'" + company + "\' and scenario = \'" + scenario + "\' and version = '';";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(update_sql_str);
    conn_ins.commit();

    return 0;




def upload_cal_results_to_financials(conn_ins, result_value_list, company, scenario, version=''):

    query_sql_str = "SELECT * FROM financials_adjustment WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\';";
    adjustment_financials_df = get_query_from_db(conn_ins, query_sql_str);

    # print (len(adjustment_financials_df));

    date_list = list(set(list(zip(*result_value_list))[4]));

    account_list = list(set(list(zip(*result_value_list))[3]));

    entity_name_list = list(set(list(zip(*result_value_list))[1]));

    date_list_str = "(";
    for a_date in date_list:
        date_list_str += "\'" + str(a_date) + "\', ";

    date_list_str = date_list_str[:-2] + ")";

    account_list_str = "(";
    for a_account in account_list:
        account_list_str += "\'" + str(a_account) + "\', ";

    account_list_str = account_list_str[:-2] + ")";

    entity_list_str = "(";
    for a_entity in entity_name_list:
        entity_list_str += "\'" + str(a_entity) + "\', ";

    entity_list_str = entity_list_str[:-2] + ")";

    upload_sql_str = "SET SQL_SAFE_UPDATES = 0;";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(upload_sql_str);
    conn_ins.commit();

    upload_sql_str = "delete from financials WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\' AND version = \'" + version + "\' AND period in " + date_list_str + " AND account in " + account_list_str + " AND entity in " + entity_list_str +  ";";

    # print (upload_sql_str);
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(upload_sql_str);
    conn_ins.commit();

    upload_sql_str =" INSERT INTO financials (company, entity, scenario, account, period, value, version) VALUES ";

    for item in result_value_list:
        temp_sql_str = "( \'" + item[0] + "\' , \'" + item[1] + "\' , \'" + item[2] + "\' , \'" + item[3] + "\' , \'" + str(item[4]) + "\' , \'" + str(item[5]) + "\' ),";
        date_obj = datetime.datetime.strptime(str(item[4]),"%Y-%m-%d").date();
        current_adjustment_financials_df = adjustment_financials_df.loc[(adjustment_financials_df['company']==item[0]) \
                                            & (adjustment_financials_df['entity']==item[1]) \
                                            & (adjustment_financials_df['scenario']==item[2]) \
                                            & (adjustment_financials_df['account']==item[3]) \
                                            & (adjustment_financials_df['period']==date_obj)];
        new_value = item[5];
        # print (len(current_adjustment_financials_df));
        # print (type(item[4]));
        if len(current_adjustment_financials_df) > 0:

            for i in range(0, len(current_adjustment_financials_df)):
                current_company = current_adjustment_financials_df.iloc[i]['company'];
                current_entity = current_adjustment_financials_df.iloc[i]['entity'];
                current_scenario = current_adjustment_financials_df.iloc[i]['scenario'];
                current_account = current_adjustment_financials_df.iloc[i]['account'];
                current_period = current_adjustment_financials_df.iloc[i]['period'];
                adjustment = current_adjustment_financials_df.iloc[i]['adjustment'];

                print ("-------------------------------------------------");
                print ("warning ! we modified: " + current_entity, current_scenario, current_account, current_period);
                print ("-------------------------------------------------");
                new_value += current_adjustment_financials_df.iloc[i]['adjustment'];


        temp_sql_str = "( \'" + item[0] + "\' , \'" + item[1] + "\' , \'" + item[2] + "\' , \'" + item[3] + "\' , \'" + str(item[4]) + "\' , \'" + str(new_value);
        temp_sql_str = temp_sql_str + "\' , \'" + version + "\' ),";

        upload_sql_str += temp_sql_str;

    upload_sql_str = upload_sql_str[:-1];

    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(upload_sql_str);
    conn_ins.commit();


    return 0;

def update_sign_financials(conn_ins, company ,scenario, version):
    reverse_sign_fsli_item_list = [item for item in AMR_SIGNS_DICT if AMR_SIGNS_DICT[item] == -1.0];

    fsli_item_str = " in ( ";

    for item in reverse_sign_fsli_item_list:
        fsli_item_str += " \'" + str(item) + "\', ";

    fsli_item_str = fsli_item_str[:-2] + " )";

    # print (fsli_item_str);

    update_sql_str = "SET SQL_SAFE_UPDATES = 0;";
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(update_sql_str);
    conn_ins.commit();

    update_sql_str = " UPDATE financials SET value = -value WHERE company = \'" + company + "\' AND scenario = \'" + scenario + "\' AND account " + fsli_item_str + ";";
    # print (update_sql_str);
    cursor = conn_ins.cursor(buffered = True);
    cursor.execute(update_sql_str);
    conn_ins.commit();


def copy_from_selected(conn_ins, company, current_scenario, selected_scenario, fsli, period_list):

    period_str = " (";

    for period in period_list:
        period_str = period_str + "\'" + period + "\' , ";

    period_str = period_str[:-2] + ")";



    delete_sql_str = "DELETE FROM financials WHERE company = \'" + company + "\' and scenario = \'" + current_scenario + "\' and version = '' and account =\'" + fsli + "\' and period in " + period_str + ";";

    print (delete_sql_str);

    # cursor = conn_ins.cursor(buffered = True);
    # cursor.execute(delete_sql_str);
    # conn_ins.commit();



    insert_sql_str = "INSERT INTO financials (company, entity, scenario, account, period, value, version) select company, entity, \'" + current_scenario + "\', account, period, value, '' \
                    from financials where company = \'" + company + "\' and scenario = \'" + selected_scenario + "\' AND account = \'" + fsli + "\' AND period in " + period_str + " and version = 'vf';"

    print (insert_sql_str);
