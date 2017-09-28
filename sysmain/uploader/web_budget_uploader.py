import pandas as pd;



SHEET_NAME_DICT = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby','HoldCo']};




def upload_budget(submit_file, company, budget_scenario):
    print (type(submit_file), company, budget_scenario);

    total_budget_upload_list = read_budget_input(submit_file, company, budget_scenario);
    print (len(total_budget_upload_list));
    return total_budget_upload_list;



def read_budget_input(budget_submit_file, company_name, budget_scenario):
    print ("----------------------   reading excel inputs...");
    budget_data_df = pd.read_excel(budget_submit_file, header = 0);
    print (len(budget_data_df));

    budget_info_header_list = ['Plant','Account No','Account Title','Model group','Project ID','Cost Component ID',\
                               'Work Order Number','Outage Code ID','Invoice ID','Contract Number ID',\
                               'Reference number','Cost Category','Cost Sub Category','Project Name'];

    budget_info_list = [];
    for budget_info_header_item in budget_info_header_list:
        budget_info_list.append(budget_data_df[budget_info_header_item]);

    budget_info_list = [list(item) for item in zip(*budget_info_list)];

    budget_upload_list = [];

    for i in range(len(budget_info_header_list), len(budget_data_df.columns)-1):
        # print (list(budget_data_df.columns)[i]);
        # print (len(budget_data_df[list(budget_data_df.columns)[i]]));

        scenario_list = [budget_scenario for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        company_list = [company_name for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        period_list = [str(list(budget_data_df.columns)[i]).split(" ")[0] for j in range(0, len(budget_data_df[list(budget_data_df.columns)[i]]))];
        value_list = list(budget_data_df[list(budget_data_df.columns)[i]]);

        temp_combine_list = [scenario_list, company_list, period_list, value_list];
        temp_combine_list = [list(item) for item in zip(*temp_combine_list)];

        temp_budget_upload_list = [list(item_a + item_b) for item_a, item_b in zip(budget_info_list, temp_combine_list)];

        # print (len(temp_budget_upload_list));

        budget_upload_list += temp_budget_upload_list;



    list_size = len(budget_upload_list);
    increment = 2000;
    remaining_size = list_size;
    start_index = 0;
    partition_list = [];
    while remaining_size > increment:
        remaining_size -= increment;
        partition_list.append((start_index, start_index+increment));
        start_index = start_index + increment;

    partition_list.append((start_index, start_index+remaining_size));


    total_budget_ready_to_kean_list = [];

    for partition in partition_list:

        filtered_budget_upload_list = [];

        for item in budget_upload_list[partition[0]:partition[1]]:

            item_company = str(item[15]);
            item_scenario = str(item[14]);
            item_entity = str(item[0]).strip();
            item_entity = item_entity if item_entity != 'HoldCO' else 'HoldCo';
            item_account = str(item[1]);
            item_account_name = str(item[2]).strip().replace("'",' ');

            item_period = str(item[16]);
            item_value = str(item[17]) if str(item[17]) != 'nan' else '0.0';


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

            nna_insert_item_list = [];

            for insert_item in insert_item_list:
                if insert_item == 'nan':
                    insert_item = '';
                nna_insert_item_list.append(insert_item);


            filtered_budget_upload_list.append(nna_insert_item_list);

        total_budget_ready_to_kean_list.append(filtered_budget_upload_list);

    return total_budget_ready_to_kean_list;


def read_budget_input_old(file_path, company_name, data_date):
    with open(file_path, 'r') as f:
        reader = csv.reader(f);
        budget_list = list(reader);

    period_range = budget_list[0][14:];

    reformat_period_range_list = [];
    for item in period_range:
        # print (item);
        new_date = datetime.datetime.strptime(item, '%m/%d/%Y').strftime('%Y-%m-%d')
        # print (new_date);
        reformat_period_range_list.append(new_date);

    budget_list = budget_list[1:];

    # for item in budget_list:
    #     print (item);

    current_entity = '';

    budget_upload_list = [];

    for i in range(0, len(budget_list)):
        budget_item = budget_list[i];
        if current_entity == '':
            current_entity = budget_item[0];
        elif budget_item[0] != '' and current_entity != budget_item[0] :
            current_entity = budget_item[0];


        current_account = budget_item[1];
        current_account_name = budget_item[2];

        for period in reformat_period_range_list:
            index = reformat_period_range_list.index(period);
            value_index = index + 14;
            value = budget_item[value_index];
            budget_upload_item = ['',company_name, current_entity, data_date, current_account, current_account_name, period, value, budget_item[3],budget_item[4],budget_item[5],budget_item[6],budget_item[7],budget_item[8],budget_item[9],budget_item[10],budget_item[11],budget_item[12],budget_item[13]];
            budget_upload_list.append(budget_upload_item);

    # for item in budget_upload_list:
    #     print (item);

    # print (len(budget_upload_list));
    return budget_upload_list;



def read_respreads_input(file_path, company_name, data_date):
    with open(file_path, 'r') as f:
        reader = csv.reader(f);
        respread_list = list(reader);

    period_range = respread_list[0][14:];

    for item in period_range:
        print (item);


    reformat_period_range_list = [];
    for item in period_range:
        # print (item);
        new_date = datetime.datetime.strptime(item, '%m/%d/%Y').strftime('%Y-%m-%d')
        # print (new_date);
        reformat_period_range_list.append(new_date);

    respread_list = respread_list[1:];

    # for item in respread_list:
        # print (item);

    # sys.exit();

    current_entity = '';

    respread_upload_list = [];

    for i in range(0, len(respread_list)):
        respread_item = respread_list[i];
        if current_entity == '':
            current_entity = respread_item[0];
        elif respread_item[0] != '' and current_entity != respread_item[0] :
            current_entity = respread_item[0];


        current_account = respread_item[1];
        current_account_name = respread_item[2];
        current_model_group = respread_item[3];
        current_project_id = respread_item[4];
        current_project_name = respread_item[13];




        for period in reformat_period_range_list:
            index = reformat_period_range_list.index(period);
            value_index = index + 14;
            value = respread_item[value_index];
            respread_upload_item = ['',company_name, current_entity, data_date, current_account, current_account_name, period, value, current_model_group, current_project_id, current_project_name];
            respread_upload_item = respread_upload_item + respread_item[5:13];
            respread_upload_list.append(respread_upload_item);


    return respread_upload_list;
