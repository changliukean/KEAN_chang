import pandas as pd;





SHEET_NAME_DICT = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby','HoldCo']};


def upload_actuals(submit_file, company, scenario):
    print (type(submit_file), company, scenario);

    print ("submit file:        ", submit_file, type(submit_file));



    total_actuals_upload_list = read_actuals_xlsx(submit_file, SHEET_NAME_DICT[company], scenario, company);
    print (len(total_actuals_upload_list));
    return total_actuals_upload_list;

def read_actuals_xlsx(file_obj, sheet_name_list, scenario, company):
    # print (file_path);
    print ("----------------------   reading excel inputs...");

    actuals_data = pd.read_excel(file_obj, sheet_name_list, header = 0);

    total_actuals_upload_list = [];
    for item in actuals_data:
        current_tab_df = actuals_data[item];
        current_input_list = [];


        column_header_list = ['AS OF DATE','ACCOUNTING MONTH','BUSINESS UNIT ID','COMPANY NAME','BVR GROUP','ACCOUNT',\
                                                     'ACCOUNT TITLE','PROJECT ID', 'COST COMPONENT ID', 'WORK ORDER NUMBER', 'OUTAGE CODE ID',\
                                                     'INVOICE ID','CONTRACT NUMBER ID','REFERENCE NUMBER','PERIOD BALANCE', 'PLANT ID', 'REPORT_DATE',\
                                                     'ENDING BALANCE','TOTAL CREDIT','TOTAL DEBIT'];

        """ optimized logic I LOVE THIS!"""
        """ reduce the read time from 50 seconds to 20 sceonds!! """
        for column_header in column_header_list:
            current_input_list.append(list(current_tab_df[column_header]));


        scenario_list = [scenario for i in range(0, len(current_tab_df))];
        company_list = [company for i in range(0, len(current_tab_df))];

        current_input_list.append(scenario_list);
        current_input_list.append(company_list);

        current_input_list = [list(item) for item in zip(*current_input_list)];
        total_actuals_upload_list += current_input_list;



    list_size = len(total_actuals_upload_list);
    increment = 2000;
    remaining_size = list_size;
    start_index = 0;
    partition_list = [];
    while remaining_size > increment:
        remaining_size -= increment;
        partition_list.append((start_index, start_index+increment));
        start_index = start_index + increment;

    partition_list.append((start_index, start_index+remaining_size));


    total_actuals_ready_to_kean_list = [];

    for partition in partition_list:


        actuals_ready_to_kean_list = [];

        for item in total_actuals_upload_list[partition[0]:partition[1]]:
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
            period_balance = float(item[14]) if str(item[14]) != 'nan' else 0.0;
            ending_balance = float(item[17]) if str(item[17]) != 'nan' else 0.0;
            total_credit = float(item[18]) if str(item[18]) != 'nan' else 0.0;
            total_debit = float(item[19]) if str(item[19]) != 'nan' else 0.0;
            # print (period_balance, ending_balance, total_credit, total_debit);
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

            for i in range(0, len(insert_item_list)):
                if str(insert_item_list[i]) == 'nan':
                    insert_item_list[i] = '';

            actuals_ready_to_kean_list.append(insert_item_list);

        total_actuals_ready_to_kean_list.append(actuals_ready_to_kean_list);

    return total_actuals_ready_to_kean_list;
