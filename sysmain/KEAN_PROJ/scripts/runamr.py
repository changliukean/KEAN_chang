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


from display import disp_controller_budget;
from display import disp_controller_actest;
from display import disp_controller_var;
from display import disp_controller_lc;
from display import disp_controller_difftest;

import sys;

# BUDGET_SCENARIO = '2017 June AMR Budget';
# AMR_SCENARIO = '2017 June AMR';
# LAST_AMR_SCENARIO = '2017 May AMR';
# COMPANY = 'Lightstone';

""" dispatch back test settings """
COMPANY = 'Lightstone';
AMR_SCENARIO = '2017 July AMR';
BUDGET_SCENARIO = '2017 June AMR Budget';
# AMR_SCENARIO = '2017 July AMR';
LAST_AMR_SCENARIO = '2017 June AMR';

VERSION = 'v1';


def db_config_part():
    """
        step 1: we configre database connection
    """
    db_config_info = db_configurator.get_db_config_info();
    # print (db_config_info);
    host = db_config_info['host'];
    user = db_config_info['user'];
    password = db_config_info['password'];
    database = db_config_info['database'];

    # db_controller.set_connection_instance_global(host,user,password,database);

    conn_ins = db_controller.set_connection_instance_global(host, user, password, database);
    return conn_ins;





if __name__ == "__main__":
    print ("------------------AMR processing-------------------");

    """
        step 1: preset the arguments for AMR
    """

    actuals_month_dates_list,\
    budget_month_dates_list,\
    estimate_month_dates_list = date_utils.get_dates_info_from_amr_scenario(AMR_SCENARIO);

    # print (actuals_month_dates_list);
    # sys.exit();
    # print (estimate_month_dates_list);

    """
        step 2: config db connection
    """
    conn_ins = db_config_part();





    """
        step 3: data input/upload to KEAN for AMR
    """

    """ new budget data and budget adjustment data upload logic is to be implemented if needed. Because budget data should not change over time """
    """ also we made a lot of hardcoded adjustment to it because the input file is not as clean as we want """
    # budget_uploader.budget_data_upload(conn_ins, COMPANY, BUDGET_SCENARIO);
    """ refactored and optimized !"""
    """ refactored with data consistency TEST !!!"""
    # actuals_uploader.actuals_data_upload(conn_ins, COMPANY, AMR_SCENARIO, LAST_AMR_SCENARIO);
    # sys.exit();
    """ refactored """
    # dispatch_uploader.dispatch_data_upload(conn_ins, COMPANY, AMR_SCENARIO);

    # respreads_uploader.respreads_data_upload(conn_ins, COMPANY, AMR_SCENARIO);
    # sys.exit();
    # general_control.direct_load_insurance_propertytax_miscincome(conn_ins, COMPANY, AMR_SCENARIO);

    # general_control.direct_load_financials(conn_ins, COMPANY, AMR_SCENARIO, 'v4');

    # general_control.direct_load_financials(conn_ins, COMPANY, AMR_SCENARIO, '');
    # sys.exit();

    """
        step 4: run business logic and upload result to kean/financials
    """
    """ refactored """
    # budget.budget_main(conn_ins, COMPANY, BUDGET_SCENARIO, 2017);
    """ refactored """
    # actuals.actuals_main(conn_ins, COMPANY, AMR_SCENARIO, actuals_month_dates_list);
    # sys.exit();
    """ refactored """
    # estimate_month_dates_list = ['2017-02-28','2017-03-31','2017-04-30','2017-05-31','2017-06-30']
    # print (estimate_month_dates_list);
    # estimate.estimate_main(conn_ins, COMPANY, AMR_SCENARIO, estimate_month_dates_list);
    # sys.exit();
    # respreads.redpreads_main(conn_ins, COMPANY, AMR_SCENARIO, BUDGET_SCENARIO, actuals_month_dates_list + estimate_month_dates_list);
    # respreads.respreads_main_details(conn_ins, COMPANY, AMR_SCENARIO, BUDGET_SCENARIO, actuals_month_dates_list + estimate_month_dates_list);
    # sys.exit();



    """ this is for the respreads """
    # amr_budget_respreads_part();
    """ this is for the hedge pnl values for estimates """
    # estimate_hedge_pnl_part();
    """ refactored """
    """ apply the adjustment to the financials """
    """ this should be a one time call, be careful not call this twice"""
    # general_control.sign_control_financials_amr(conn_ins,COMPANY, AMR_SCENARIO, '');
    # general_control.sign_control_financials_amr(conn_ins,COMPANY, LAST_AMR_SCENARIO, 'vf');





    """
        step 5: after all calculations are done, we do calcs as the last step. to make sure calcs are up-to-date
        also this step can be run separately if we changed some values directly to the KEAN/financials table
    """

    """ refactored """
    """ update calcs for actest"""
    # print (actuals_month_dates_list);
    # db_controller.update_financials_calcs(conn_ins, LAST_AMR_SCENARIO, COMPANY, actuals_month_dates_list+estimate_month_dates_list, 'vf');
    # forecast_date_range_list = date_utils.get_month_dates_list(2017,1,12);
    # forecast_date_range_list = date_utils.get_month_dates_list(2018,1,12);
    # forecast_date_range_list += date_utils.get_month_dates_list(2019,1,12);
    # forecast_date_range_list += date_utils.get_month_dates_list(2020,1,12);
    # forecast_date_range_list += date_utils.get_month_dates_list(2021,1,12);
    # print (forecast_date_range_list);
    # # # #
    # # # estimate.estimate_main(conn_ins, COMPANY, AMR_SCENARIO, forecast_date_range_list);
    # db_controller.update_financials_calcs(conn_ins, AMR_SCENARIO, COMPANY, forecast_date_range_list, 'v5');
    # # sys.exit();
    """ update calcs for budget"""
    # general_control.sign_control_financials_amr(conn_ins,COMPANY, BUDGET_SCENARIO);
    # db_controller.update_financials_calcs(conn_ins, BUDGET_SCENARIO, COMPANY, budget_month_dates_list);

    # sys.exit();
    """
        step 6: versioning the financials and one time sign midification
    """
    # general_control.version_current_financials(conn_ins, COMPANY, AMR_SCENARIO, 'v5');
    # sys.exit();
    # db_controller.update_financials_calcs(conn_ins, AMR_SCENARIO, COMPANY, actuals_month_dates_list + estimate_month_dates_list, 'v1');
    # sys.exit();
    # db_controller.update_financials_calcs(conn_ins, LAST_AMR_SCENARIO, COMPANY, actuals_month_dates_list + estimate_month_dates_list , 'v1');

    """
        step 7: generate output reports
    """
    """ refactored """
    # disp_controller_budget.budget_report(conn_ins, COMPANY, AMR_SCENARIO, 2021);
    """ refactored """
    # amr_version = 'v5';
    # budget_version = 'v1';
    # disp_controller_actest.actest_report(conn_ins, COMPANY, AMR_SCENARIO, amr_version, BUDGET_SCENARIO, budget_version);
    # amr_version = 'v4';
    # budget_version = 'v1';
    # disp_controller_var.variance_report(conn_ins, COMPANY, AMR_SCENARIO, amr_version, BUDGET_SCENARIO, budget_version, actuals_month_dates_list);

    """ refactored """
    """ generating result comparison reports """

    """ test case 1 """
    """ if there is no version number specified, simply compare two scenarios with no version info"""
    # first_scenario = AMR_SCENARIO;
    # second_scenario = BUDGET_SCENARIO;
    # disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, start_month = 2, end_month = 6);

    """ test case 2 """
    """ different scenarios and different version numbers """
    # first_scenario = LAST_AMR_SCENARIO;
    # second_scenario = BUDGET_SCENARIO;
    # # disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, first_version = VERSION, start_month = 2, end_month = 6);
    # disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, first_version = 'v1', second_version = 'v2', start_month = 1, end_month = 12);

    """ test case 3 """
    """ same scenario but different version numbers"""
    # first_scenario = BUDGET_SCENARIO;
    # second_scenario = BUDGET_SCENARIO;
    # second_version = 'v3';
    # disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, first_version = VERSION, second_version = second_version, start_month = 1, end_month = 12);
    #
    """ July AMR comparison """
    # first_scenario = AMR_SCENARIO;
    # first_version = 'v4';
    # second_scenario = LAST_AMR_SCENARIO;
    # second_version = 'vf';
    # disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, first_version = first_version, second_version = second_version, start_month = 1, end_month = 12);

    first_scenario = AMR_SCENARIO;
    first_version = '';
    second_scenario = AMR_SCENARIO;
    second_version = 'v4';
    disp_controller_difftest.difftest_report(conn_ins, COMPANY, first_scenario, second_scenario, first_version = first_version, second_version = second_version, start_month = 1, end_month = 12);

    #


    """
        step 8: generate support reports
    """

    # disp_controller_lc.letters_of_credit_report(conn_ins, COMPANY);
