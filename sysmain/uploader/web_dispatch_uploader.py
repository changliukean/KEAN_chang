import pandas as pd;





SHEET_NAME_DICT = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby']};


def upload_dispatch(submit_file, company, scenario):


    tab_name_list = SHEET_NAME_DICT[company];


    dispatch_list = [];
    for tab_name in tab_name_list:
        result_list = read_dispatch_data_from_xlsx(submit_file, tab_name, scenario, company);
        dispatch_list += result_list;

    print (len(dispatch_list));

    return dispatch_list;



def read_dispatch_data_from_xlsx(xlsx_file_path, tab_name, scenario, company):
    dispatch_df = pd.read_excel(xlsx_file_path, tab_name, header=None);
    result_list = [];
    for i in range(1, len(dispatch_df)):
        for j in range(1, len(dispatch_df.iloc[i])):
            # print (dispatch_df.iloc[i][0]);
            result_list.append([scenario, tab_name, dispatch_df.iloc[i][0], str(dispatch_df.iloc[0][j]).split(" ")[0], dispatch_df.iloc[i][j], company]);


    return result_list;
