import sys;
import os;
from pathlib import Path;
import pandas as pd;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller;

import datetime;


def version_current_financials(conn_ins,company, scenario, version):
    db_controller.update_version_info_financials(conn_ins,company, scenario, version);





def sign_control_financials_amr(conn_ins,company, amr_scenario, version=''):
    db_controller.update_sign_financials(conn_ins, company, amr_scenario, version);





def sign_control_financials_budget(conn_ins, company, budget_scenario, version=''):
    sign_control_financials_amr(conn_ins, company, budget_scenario, version);



def direct_load_insurance_propertytax_miscincome(conn_ins, company, scenario, version=''):
    direct_file_input_folder = str(Path(__file__).parents[2]) + '\data\direct';

    direct_upload_file_list = os.listdir(direct_file_input_folder);
    for direct_file in direct_upload_file_list:
        full_file_path = os.path.join(direct_file_input_folder, direct_file);
        if company in full_file_path and '~' not in full_file_path and 'direct' in direct_file:
            # print (full_file_path);
            direct_upload_financials_list = read_direct_input(full_file_path, company, scenario);

            print (len(direct_upload_financials_list));

            for item in direct_upload_financials_list:
                print (item);

            db_controller.upload_cal_results_to_financials(conn_ins, direct_upload_financials_list, company, scenario, version);


def read_direct_input(full_file_path, company, scenario):

    upload_to_financials_list = [];


    direct_data_df = pd.read_excel(full_file_path, header = 0);
    # print (len(direct_data_df));
    actuals_month_dates_list, fullyear_month_dates_list, estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(scenario);
    # for item in direct_data_df:
    #     print (item);

    # print (direct_data_df.iloc[0][0])
    # print (direct_data_df.iloc[0][2])
    # print (direct_data_df.iloc[2][0])

    row_number = 0;
    col_number = 0;
    while True:

        if estimate_month_dates_list[0] in str(direct_data_df.iloc[row_number][col_number]):
            # print (row_number, col_number, direct_data_df.iloc[row_number][col_number]);
            break;
        col_number += 1;

    col_number_list = range(col_number, col_number + len(estimate_month_dates_list) );

    # for item in col_number_list:
    #     print (item);

    col_number = 0;
    row_number = 0;
    while True:
        if 'LOAD TO FORECAST' in str(direct_data_df.iloc[row_number][col_number]):
            # print (row_number, col_number, direct_data_df.iloc[row_number][col_number]);
            break;
        row_number += 1;

    row_number = row_number + 1;


    insurance_row = [];
    entity_list = [];
    for row in range(row_number, row_number + 4):
        # print (str(direct_data_df.iloc[row][3]));
        entity = str(direct_data_df.iloc[row][3]).strip();
        entity_list.append(entity);
        insurance_row.append(row);

    # print (col_number_list);
    # print (entity_list);
    # print (insurance_row);


    for i in range(0, len(entity_list)):
        entity = entity_list[i];
        for col in col_number_list:
            # print (entity, str(direct_data_df.iloc[0][col]).split(" ")[0],str(direct_data_df.iloc[insurance_row[i]][col]));
            """
                (company, entity, scenario, account, period, value, version)
            """
            upload_to_financials_list.append([company, entity, scenario,  'Insurance', str(direct_data_df.iloc[0][col]).split(" ")[0],str(direct_data_df.iloc[insurance_row[i]][col])]);

    ###################################################################################
    ###################################################################################
    ###################################################################################

    direct_data_df = pd.read_excel(full_file_path, sheetname=1, header = 0);

    row_number = 0;
    while True:
        print (row_number);
        if 'Property Taxes' in str(direct_data_df.iloc[row_number][2]):
            # print (row_number, 0, direct_data_df.iloc[row_number][2]);
            break;
        row_number += 1;

    row_number = row_number - 1;
    print (row_number);
    col_number = 0;
    while True:
        # print (col_number);
        if estimate_month_dates_list[0] in str(direct_data_df.iloc[row_number][col_number]):
            # print (row_number, col_number, direct_data_df.iloc[row_number][col_number]);
            break;
        col_number += 1;

    col_number_list = range(col_number, col_number + len(estimate_month_dates_list) );

    # print (col_number_list);


    for row in range(row_number+1, row_number+5):
        entity = str(direct_data_df.iloc[row][3]);
        # print (entity);
        for i in range(0,len(col_number_list)):
            col = col_number_list[i];
            """
                (company, entity, scenario, account, period, value, version)
            """
            value = str(abs(float(str(direct_data_df.iloc[row][col]))));
            upload_to_financials_list.append([company, entity, scenario, 'Property Tax', estimate_month_dates_list[i],value]);
            # print ([company, entity, scenario, 'Property Tax', estimate_month_dates_list[i],value]);


    ###################################################################################
    ###################################################################################
    ###################################################################################

    direct_data_df = pd.read_excel(full_file_path, sheetname=2, header = 0);

    row_number = 0;
    while True:
        print (row_number);
        if 'Other Income' in str(direct_data_df.iloc[row_number][2]):
            # print (row_number, 0, direct_data_df.iloc[row_number][2]);
            break;
        row_number += 1;

    row_number = row_number - 1;
    print (row_number);
    col_number = 0;
    while True:
        # print (col_number);
        if estimate_month_dates_list[0] in str(direct_data_df.iloc[row_number][col_number]):
            # print (row_number, col_number, direct_data_df.iloc[row_number][col_number]);
            break;
        col_number += 1;

    col_number_list = range(col_number, col_number + len(estimate_month_dates_list) );

    print (col_number_list);


    for row in range(row_number+1, row_number+2):
        entity = str(direct_data_df.iloc[row][3]);
        # print (entity);
        for i in range(0,len(col_number_list)):
            col = col_number_list[i];
            """
                (company, entity, scenario, account, period, value, version)
            """
            value = str(abs(float(str(direct_data_df.iloc[row][col]))));
            upload_to_financials_list.append([company, entity, scenario, 'Misc Income', estimate_month_dates_list[i],value]);
            # print ([company, entity, scenario, 'Misc Income', estimate_month_dates_list[i],value]);

    upload_to_financials_list += hardcode_fixed_fuel();

    return upload_to_financials_list;




def hardcode_fixed_fuel():
    upload_to_financials_list = [['Lightstone', 'Darby', '2017 July AMR', 'Fixed Fuel', '2017-08-31', '211000'],
                                 ['Lightstone', 'Darby', '2017 July AMR', 'Fixed Fuel', '2017-09-30', '211000'],
                                 ['Lightstone', 'Darby', '2017 July AMR', 'Fixed Fuel', '2017-10-31', '63300'],
                                 ['Lightstone', 'Darby', '2017 July AMR', 'Fixed Fuel', '2017-11-30', '-0'],
                                 ['Lightstone', 'Darby', '2017 July AMR', 'Fixed Fuel', '2017-12-31', '-0'],
                                 ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Fixed Fuel', '2017-08-31', '1585836'],
                                 ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Fixed Fuel', '2017-09-30', '1534680'],
                                 ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Fixed Fuel', '2017-10-31', '1585836'],
                                 ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Fixed Fuel', '2017-11-30', '1534680'],
                                 ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Fixed Fuel', '2017-12-31', '1585836']];


    upload_to_financials_list += [['Lightstone', 'Gavin', '2017 July AMR', 'Capacity Revenue', '2017-08-31', '11795729.4'],
                                  ['Lightstone', 'Gavin', '2017 July AMR', 'Capacity Revenue', '2017-09-30', '11415222'],
                                  ['Lightstone', 'Gavin', '2017 July AMR', 'Capacity Revenue', '2017-10-31', '11795729.4'],
                                  ['Lightstone', 'Gavin', '2017 July AMR', 'Capacity Revenue', '2017-11-30', '11415222'],
                                  ['Lightstone', 'Gavin', '2017 July AMR', 'Capacity Revenue', '2017-12-31', '11795729.4'],
                                  ['Lightstone', 'Waterford', '2017 July AMR', 'Capacity Revenue', '2017-08-31', '3946468.95'],
                                    ['Lightstone', 'Waterford', '2017 July AMR', 'Capacity Revenue', '2017-09-30', '3819163.5'],
                                    ['Lightstone', 'Waterford', '2017 July AMR', 'Capacity Revenue', '2017-10-31', '3946468.95'],
                                    ['Lightstone', 'Waterford', '2017 July AMR', 'Capacity Revenue', '2017-11-30', '3819163.5'],
                                    ['Lightstone', 'Waterford', '2017 July AMR', 'Capacity Revenue', '2017-12-31', '3946468.95'],
                                    ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Capacity Revenue', '2017-08-31', '4889995.8'],
                                    ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Capacity Revenue', '2017-09-30', '4732254'],
                                    ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Capacity Revenue', '2017-10-31', '4889995.8'],
                                    ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Capacity Revenue', '2017-11-30', '4732254'],
                                    ['Lightstone', 'Lawrenceburg', '2017 July AMR', 'Capacity Revenue', '2017-12-31', '4889995.8'],
                                    ['Lightstone', 'Darby', '2017 July AMR', 'Capacity Revenue', '2017-08-31', '2123580.6'],
                                    ['Lightstone', 'Darby', '2017 July AMR', 'Capacity Revenue', '2017-09-30', '2055078'],
                                    ['Lightstone', 'Darby', '2017 July AMR', 'Capacity Revenue', '2017-10-31', '2123580.6'],
                                    ['Lightstone', 'Darby', '2017 July AMR', 'Capacity Revenue', '2017-11-30', '2055078'],
                                    ['Lightstone', 'Darby', '2017 July AMR', 'Capacity Revenue', '2017-12-31', '2123580.6']]


    return upload_to_financials_list


DIRECT_UPLOAD_INPUT_FOLDER = str(Path(__file__).parents[2]) + '\data\manual_financials';


def direct_load_financials(conn_ins, company, scenario, version = ''):
    print ("=================   uploading labor data to kean...");
    respreads_file_input_folder = DIRECT_UPLOAD_INPUT_FOLDER;
    respreads_input_file_list = os.listdir(respreads_file_input_folder);
    for respreads_file in respreads_input_file_list:
        full_file_path = os.path.join(respreads_file_input_folder, respreads_file);
        if company in full_file_path and '~' not in full_file_path and 'manual' in respreads_file:
            print (full_file_path);
            respreads_upload_list = read_respreads_input(full_file_path, company, scenario);
            db_controller.upload_cal_results_to_financials(conn_ins, respreads_upload_list, company, scenario, version);


def read_respreads_input(full_file_path, company, scenario):
    respreads_data_df = pd.read_excel(full_file_path, header = 0);
    print (len(respreads_data_df));
    input_date = date_utils.get_dates_info_from_amr_scenario(scenario)[0][-1];
    respreads_upload_list = [];
    """
        account
    """

    print (input_date);

    for item in respreads_data_df:
        if isinstance(item, datetime.datetime):
            if str(item).split(" ")[0] > input_date:
                # print (item);
                # value_list.append(list(respreads_data_df[item]));
                for i in range(0, len(respreads_data_df)):
                    respreads_upload_list.append([company] + [list(respreads_data_df.iloc[i][['Entity','FSLI']])[0]] + [scenario] + [list(respreads_data_df.iloc[i][['Entity','FSLI']])[1]] + [str(item).split(" ")[0],str(respreads_data_df[item].iloc[i])]);

    for item in respreads_upload_list:
        print (item);

    print (len(respreads_upload_list));

    return respreads_upload_list;
