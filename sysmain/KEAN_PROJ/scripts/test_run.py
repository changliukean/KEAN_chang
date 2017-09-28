from utility import date_utils;
from database import db_controller;
from django.db import connection;



from utility import date_utils;
from database import db_configurator;
from database import db_controller;


from input import budget_uploader;
from input import actuals_uploader;
from input import dispatch_uploader;
from input import respreads_uploader;


from logic import budget;
from logic import actuals;
from logic import estimate;
from logic import general_control;
from logic import respreads;
from logic import liquidity;
from logic import hedge;
from logic import respreads;
from logic import labor;
from logic import support;


from display import disp_controller_fy;
from display import disp_controller_actest;
from display import disp_controller_var;
from display import disp_controller_lc;
from display import disp_controller_difftest;
from display import disp_controller_liquidity;
from display import disp_controller_hedge;
from display import disp_controller_support;






import time;






def db_config_part(django_connection_dict):
    """
        step 1: we configre database connection
    """

    host = django_connection_dict['HOST'];
    user = django_connection_dict['USER'];
    password = django_connection_dict['PASSWORD'];
    database = django_connection_dict['NAME'];

    # db_controller.set_connection_instance_global(host,user,password,database);

    conn_ins = db_controller.set_connection_instance_global(host, user, password, database);
    return conn_ins;

def test_run_actuals(company, amr_scenario):
    # print (amr_scenario);
    actuals_month_dates_list,\
    budget_month_dates_list,\
    estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario);
    # print (estimate_month_dates_list);

    conn_ins = db_config_part(connection.settings_dict);
    print ("actuals function called..............................................");
    # actuals.actuals_main(conn_ins, company, amr_scenario, actuals_month_dates_list);

def test_run_budget(company, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    current_year = int(budget_scenario.split(" ")[0]);
    year_list = list(range(current_year, current_year+5));
    print (year_list);

    print ("budget function called..............................................");
    for year in year_list:
        print (year);

        budget.budget_main(conn_ins, company, budget_scenario, year);



def test_run(company, amr_scenario, budget_scenario, amr_version, budget_version):

    # db_name = connection.settings_dict;
    # print (db_name);
    conn_ins = db_config_part(connection.settings_dict);
    # print (conn_ins);

    # respreads.respreads_main_details(conn_ins, company, amr_scenario, budget_scenario, actuals_month_dates_list + estimate_month_dates_list);

    first_scenario = amr_scenario;
    first_version = '';
    second_scenario = amr_scenario;
    second_version = 'v4';
    disp_controller_difftest.difftest_report(conn_ins, company, first_scenario, second_scenario, first_version = first_version, second_version = second_version, start_month = 1, end_month = 12);



def kean_proj_upload_actuals(company, amr_scenario):
    conn_ins = db_config_part(connection.settings_dict);
    actuals_uploader.actuals_data_upload(conn_ins, company, amr_scenario);

def kean_proj_upload_dispatch(company, amr_scenario):
    conn_ins = db_config_part(connection.settings_dict);
    dispatch_uploader.dispatch_data_upload(conn_ins, company, amr_scenario);

def kean_proj_upload_respreads(company, amr_scenario):
    conn_ins = db_config_part(connection.settings_dict);
    respreads_uploader.respreads_data_upload(conn_ins, company, amr_scenario);

def kean_proj_run_budget(company, amr_scenario, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    year_list = list(range(int(amr_scenario.split(" ")[0]), int(amr_scenario.split(" ")[0])+5));

    for year in year_list:
        print (year);
        budget.budget_main(conn_ins, company, amr_scenario, budget_scenario, year);





def kean_proj_run_budget_for_forecast_period(company, amr_scenario, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    year_list = list(range(int(amr_scenario.split(" ")[0])+1, int(amr_scenario.split(" ")[0])+5));


    budget.budget_main_forecast(conn_ins, company, amr_scenario, budget_scenario, year_list);





def kean_proj_run_dispatch(company, amr_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    print (company, amr_scenario);

    forecast_year_list = list(range(int(amr_scenario.split(" ")[0])+1, int(amr_scenario.split(" ")[0])+5));

    print ("we are at DISPATCH", company, amr_scenario, forecast_year_list);

    estimate_plus_forecast_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[2];

    for selected_year in forecast_year_list:
        estimate_plus_forecast_month_dates_list += date_utils.get_month_dates_list(selected_year,1,12);


    estimate.estimate_main(conn_ins, company, amr_scenario, estimate_plus_forecast_month_dates_list)


def kean_proj_run_actuals(company, amr_scenario):
    conn_ins = db_config_part(connection.settings_dict);
    print ("we are at ACTUALS", company, amr_scenario);

    actuals_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[0];
    actuals.actuals_main(conn_ins, company, amr_scenario, actuals_month_dates_list);




def kean_proj_run_diff_report(company, first_scenario, second_scenario, first_version, second_version, first_year, second_year):
    conn_ins = db_config_part(connection.settings_dict);
    download_file_path = disp_controller_difftest.difftest_report(conn_ins, company, first_scenario, second_scenario, first_version, second_version, first_year, second_year);

    return download_file_path;








def kean_proj_run_amr_report(company, amr_scenario, amr_version, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    download_report_file_path = disp_controller_actest.actest_report(conn_ins, company, amr_scenario, amr_version, budget_scenario, 'vf');

    return download_report_file_path;

def kean_proj_run_variance_report(company, amr_scenario, amr_version, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    actuals_month_dates_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[0];

    download_file_path_ytd, download_file_path_mtd = disp_controller_var.variance_report(conn_ins, company, amr_scenario, amr_version, budget_scenario, 'vf', actuals_month_dates_list);

    return download_file_path_ytd, download_file_path_mtd;


def kean_proj_run_fy_report(selected_company, selected_scenario, selected_version, selected_year):
    conn_ins = db_config_part(connection.settings_dict);
    download_report_file_path = disp_controller_fy.full_year_report(conn_ins, selected_company, selected_scenario, selected_year, version = selected_version);
    return download_report_file_path;



def kean_proj_run_liquidity(selected_scenario, selected_company, amr_version, valuation_date):
    conn_ins = db_config_part(connection.settings_dict);

    start_time = time.time();


    # print (conn_ins);


    df_liquidity, tax_depreciation_result, maintenance_capex_dict, ltsa_capex_dict = liquidity.process_liquidity(conn_ins, selected_scenario, selected_company, amr_version, valuation_date);


    print (" start to generate report ");
    print (len(tax_depreciation_result));
    # print (maintenance_capex_dict);


    liquidity_report_file_path = disp_controller_liquidity.liquidity_report(df_liquidity, selected_scenario, selected_company, maintenance_capex_dict, ltsa_capex_dict);
    debt_balance_report_file_path = disp_controller_liquidity.debt_balance_report(df_liquidity, selected_scenario, selected_company);
    interest_expense_report_file_path = disp_controller_liquidity.interest_expense_report(df_liquidity, selected_scenario, selected_company);
    est_tax_dist_report_file_path = disp_controller_liquidity.est_tax_dist_report(df_liquidity, tax_depreciation_result, selected_scenario, selected_company);
    print ('---------------------' + str(time.time()-start_time) + ' seconds --------------------');
    return liquidity_report_file_path, debt_balance_report_file_path, interest_expense_report_file_path, est_tax_dist_report_file_path;







def kean_proj_run_hedge(selected_scenario, selected_company):
    conn_ins = db_config_part(connection.settings_dict);


    df_hedges, df_all_prices, df_hours_pjm = hedge.process_hedge(conn_ins, selected_company, selected_scenario, upload_to_kean=True);

    print (len(df_hedges));
    disp_controller_hedge.hedge_report(df_hedges, df_all_prices,df_hours_pjm, selected_scenario, selected_company);



def kean_proj_run_respreads(selected_company, amr_scenario, budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);

    respreads_period_range_list = date_utils.get_dates_info_from_amr_scenario(amr_scenario)[1];

    print (respreads_period_range_list);

    respreads.respreads_main_details(conn_ins, selected_company, amr_scenario, budget_scenario, respreads_period_range_list)



def kean_proj_run_labor(selected_scenario, selected_company):
    conn_ins = db_config_part(connection.settings_dict);

    upload_to_financials_labor_expense_list, support_document_labor_expense_list = labor.process_labor(conn_ins, selected_scenario, selected_company);


    for item in upload_to_financials_labor_expense_list:
        print (item);

    db_controller.upload_cal_results_to_financials(conn_ins, upload_to_financials_labor_expense_list, selected_company, selected_scenario);


    # disp_controller_labor.labor_report(support_document_labor_expense_list, SCENARIO, COMPANY);




def kean_proj_make_version(selected_scenario, selected_company, version, amr_year=True):
    conn_ins = db_config_part(connection.settings_dict);

    current_year = int(selected_scenario.split(" ")[0]);

    year_range = list(range(current_year, current_year+5));

    if amr_year:
        for temp_year in year_range[:1]:
            month_dates_list = date_utils.get_month_dates_list(temp_year, 1, 12);
            print (month_dates_list);
            db_controller.update_financials_calcs(conn_ins, selected_scenario, selected_company, month_dates_list);

    else:
        for temp_year in year_range:
            month_dates_list = date_utils.get_month_dates_list(temp_year, 1, 12);
            print (month_dates_list);
            db_controller.update_financials_calcs(conn_ins, selected_scenario, selected_company, month_dates_list);

    if version != '':
        db_controller.update_version_info_financials(conn_ins, selected_company, selected_scenario, version);



def kean_proj_run_pxq(selected_company, selected_scenario, amr_version, selected_budget_scenario):
    conn_ins = db_config_part(connection.settings_dict);
    pxq_pnl_ready_list, pxq_mtd_ready_list, pxq_ytd_ready_list, pxq_forecast_ready_list, af_monthly_list, budget_monthly_list = support.pxq_main(conn_ins, selected_company, selected_scenario, amr_version, selected_budget_scenario, 'vf');
    output_report_file_path = disp_controller_support.support_pxq_report(conn_ins, selected_company, selected_scenario, pxq_pnl_ready_list, pxq_mtd_ready_list, pxq_ytd_ready_list, pxq_forecast_ready_list, af_monthly_list, budget_monthly_list);
    return output_report_file_path;



def kean_proj_copy_from_selected(selected_company, current_scenario, selected_scenario, fsli, module):
    conn_ins = db_config_part(connection.settings_dict);

    actuals_month_dates_list,\
    budget_month_dates_list,\
    estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(selected_scenario);

    selected_period_list = [];

    current_year = int(selected_scenario.split(" ")[0]);

    year_range = list(range(current_year+1, current_year+5));

    forecast_month_dates_list = [];

    for temp_year in year_range:
        forecast_month_dates_list += date_utils.get_month_dates_list(temp_year, 1, 12);


    if module == 'actual':
        selected_period_list = actuals_month_dates_list;
    if module == 'estimate':
        selected_period_list = estimate_month_dates_list;
    if module == 'forecast':
        selected_period_list = forecast_month_dates_list;
    if module == 'full':
        selected_period_list = budget_month_dates_list;
    if module == 'est_forecast':
        selected_period_list = estimate_month_dates_list + forecast_month_dates_list;

    print (module, selected_period_list);


    db_controller.copy_from_selected(conn_ins, selected_company, current_scenario, selected_scenario, fsli, selected_period_list);
