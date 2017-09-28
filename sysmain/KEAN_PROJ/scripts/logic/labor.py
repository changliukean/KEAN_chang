import sys;
from pathlib import Path;
import datetime;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/database');
import db_controller_labor;

sys.path.insert(0, str(Path(__file__).parents[1])+r'/utility');
import date_utils;


COMPANY_ENTITY_MAPPING = {'Lightstone':['Gavin','Waterford','Lawrenceburg','Darby']}

PAY_CYCLES_ANNUAL = 26;
INCENTIVE_PERCENTAGE = 0.1;
FRINGE_PERCENTAGE = 0.35;
OVERTIME_PERCENTAGE = 0.15;




""" later on move these assumptions to kean """
ASSUMPTIONS_VALUE_DICT = {'Gavin':{'severence':[["2017-08-31",168809.01],["2017-09-30",393652.31],["2018-01-31",129271.0436],["2018-09-30",1847904]],
                                   'ldw_credit':[["2018-12-31",-516.909329403851]],
                                   'retiree_medical':[["2018-09-30",2816512]]}}

ESCALATION_ASSUMPTION_PERCENTAGE = 0.025;



def process_labor(conn_ins, scenario, company):
    census_df = db_controller_labor.get_census(conn_ins, scenario, company);
    headcount_df = db_controller_labor.get_headcount(conn_ins, scenario, company)

    print (len(census_df));
    print (len(headcount_df));

    entity_name_list = COMPANY_ENTITY_MAPPING[company];
    estimate_month_dates = date_utils.get_dates_info_from_amr_scenario(scenario)[2];

    current_year = int(scenario.split(" ")[0]);

    year_range = list(range(current_year+1, current_year+5));

    forecast_month_dates_list = [];

    for temp_year in year_range:
        forecast_month_dates_list += date_utils.get_month_dates_list(temp_year, 1, 12);

    # print (estimate_month_dates);

    estimate_month_dates = estimate_month_dates + forecast_month_dates_list;

    # for item in estimate_month_dates:
    #     print (item);

    upload_to_financials_labor_expense_list = [];
    support_document_labor_expense_list = [];


    for entity in entity_name_list:
        entity_census_df = census_df.loc[census_df['default_department'].str.contains(entity.upper())];
        entity_headcount_df = headcount_df.loc[headcount_df['entity']==entity];
        print (len(entity_census_df));
        print (len(entity_headcount_df));
        for period in estimate_month_dates:
            # print (int(datetime.datetime.strptime(period,"%Y-%m-%d").date()));
            period_entity_headcount_df = entity_headcount_df.loc[entity_headcount_df['period']==datetime.datetime.strptime(period,"%Y-%m-%d").date()]
            # print (len(period_entity_headcount_df));
            headcount = period_entity_headcount_df.iloc[0]['headcount'];
            payroll_cycles = period_entity_headcount_df.iloc[0]['payroll_cycles'];
            basesalary = (sum(list(entity_census_df['salary']))/(len(entity_census_df))) * headcount * (payroll_cycles/PAY_CYCLES_ANNUAL);

            if entity == 'Gavin' and int(period.split("-")[0]) > 2018:
                basesalary = basesalary * 1.025 ** (int(period.split("-")[0]) - 2018);

            if entity != 'Gavin' and int(period.split("-")[0]) > 2017:
                basesalary = basesalary * 1.025 ** (int(period.split("-")[0]) - 2017);


            incentive = basesalary * INCENTIVE_PERCENTAGE;
            fringe = basesalary * FRINGE_PERCENTAGE;
            overtime = basesalary * OVERTIME_PERCENTAGE;
            ldw_credit = 0.0;
            severence = 0.0;
            retention = 0.0;
            retiree_medical = 0.0;
            if entity in ASSUMPTIONS_VALUE_DICT:
                if 'ldw_credit' in ASSUMPTIONS_VALUE_DICT[entity]:
                    ldw_credit = [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['ldw_credit'] if item[0] == period][0] if [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['ldw_credit'] if item[0] == period]!=[] else ldw_credit;
                if 'severence' in ASSUMPTIONS_VALUE_DICT[entity]:
                    severence =  [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['severence'] if item[0] == period][0] if [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['severence'] if item[0] == period] !=[] else severence;
                if 'retention' in ASSUMPTIONS_VALUE_DICT[entity]:
                    retention =  [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['retention'] if item[0] == period][0] if [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['retention'] if item[0] == period] !=[] else retention;
                if 'retiree_medical' in ASSUMPTIONS_VALUE_DICT[entity]:
                    retiree_medical = [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['retiree_medical'] if item[0] == period][0] if [item[1] for item in ASSUMPTIONS_VALUE_DICT[entity]['retiree_medical'] if item[0] == period] !=[] else retiree_medical;
            # print (entity, ldw_credit, severence, retention, retiree_medical);

            # print (entity, period, basesalary, incentive, fringe, overtime, ldw_credit, severence, retention, retiree_medical);
            support_document_labor_expense_list.append([entity, period, basesalary, incentive, fringe, overtime, ldw_credit, severence, retention, retiree_medical, headcount, payroll_cycles]);
            """
                (company, entity, scenario, account, period, value, version)
            """
            labor_expenses = sum([basesalary, incentive, fringe, overtime, ldw_credit, severence, retention, retiree_medical]);

            upload_to_financials_labor_expense_list.append([company, entity, scenario, 'Labor Expenses', period, labor_expenses]);

    # for item in support_document_labor_expense_list:
    #     print (item);
    # print ("=======================================================");
    #
    # for item in upload_to_financials_labor_expense_list:
    #     print (item);

    return upload_to_financials_labor_expense_list,support_document_labor_expense_list;
