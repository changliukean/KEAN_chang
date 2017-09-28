from django.shortcuts import render, redirect;
from django.http import HttpResponse, HttpResponseRedirect, Http404;
from .models import *;
from .forms import *;
from django.urls import reverse;
from django.contrib.auth.decorators import login_required;
from django.contrib.staticfiles.templatetags.staticfiles import static;
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger;
from django.db import connection;
from django.views.decorators.csrf import csrf_exempt;
from django.core.files.storage import FileSystemStorage;
from django.conf import settings;
from django.utils.encoding import smart_str;

import os;

import json;
import requests;
import sys;
import calendar;
import pandas as pd;
import datetime;


from pathlib import Path;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/sysmain/KEAN_PROJ/scripts');
import test_run;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/sysmain/KEAN_PROJ/scripts/utility');
import date_utils;


sys.path.insert(0, str(Path(__file__).parents[1])+r'/sysmain/uploader');
import web_actuals_uploader;
import web_dispatch_uploader;
import web_respreads_uploader;
import web_prices_uploader;
import web_other_uploader;
import web_budget_uploader;





from datetime import date;



MONTH_NUMBER_DICT = {'January':1,'Febuary':2,'March':3,'April':4,\
                     'May':5,'June':6,'July':7,'August':8,\
                     'September':9,'October':10,'November':11,'December':12};


""" if user is inactive for 3000 seconds, session will be timed out """
SESSION_EXPIRE_SECONDS = 3000;

@login_required(redirect_field_name='', login_url='/')
def load_sys_mainpage(request):
    request.session.set_expiry(SESSION_EXPIRE_SECONDS);
    if not request.user.is_authenticated():
        return redirect('/login/');
    else:
        existing_company_scenario_list = get_company_scenario_list();
        return render(request, 'sys_mainpage_checkview.html', {'user_name':str(request.user),'existing_company_scenario_list':existing_company_scenario_list});


@login_required(redirect_field_name='', login_url='/')
def load_sys_mainpage_pjmlmp(request):
    request.session.set_expiry(SESSION_EXPIRE_SECONDS);
    if not request.user.is_authenticated():
        return redirect('/login/');
    else:
        latest_lmp_info_list = [];
        with connection.cursor() as cursor:
            cursor.execute("select b.company, b.power_plant_name, b.pnode_id, a.valuation_date, a.dart from kean.lmp a join kean.power_plants b on a.pnode_id = b.pnode_id where a.valuation_date = (select max(valuation_date) from kean.lmp) group by a.pnode_id, a.dart;");
            for row in cursor.fetchall():
                latest_lmp_info_list.append([row[0],row[1],row[2],str(row[3]),row[4]]);

        return render(request, 'sys_mainpage_pjmlmp.html', {'user_name':str(request.user), 'latest_lmp_info_list':latest_lmp_info_list});



@login_required(redirect_field_name='', login_url='/')
def load_sys_amr_dashboard(request):
    request.session.set_expiry(SESSION_EXPIRE_SECONDS);

    if not request.user.is_authenticated():
        return redirect('/login/');
    else:
        existing_company_scenario_list = get_company_scenario_list();
        entity_list = get_all_entity(existing_company_scenario_list[0].split("-")[0], existing_company_scenario_list[0].split("-")[1]);


        # for item in existing_company_scenario_list:
        #     print (item);
        #
        # for item in entity_list:
        #     print (item);

        entity_list = ["Summary"] + entity_list;

        return render(request, 'sys_amr_dashboard.html', {'user_name':str(request.user), 'existing_company_scenario_list':existing_company_scenario_list, 'entity_list':entity_list});


@login_required(redirect_field_name='', login_url='/')
def plot_bvr(request, selected_com_scen, selected_entity, selected_fsli):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];


    af_value_list = [];
    budget_value_list = [];

    end_date_str = selected_scenario.split(" ")[0] + "-12-31";


    if selected_entity == 'Summary':
        with connection.cursor() as cursor:
            cursor.execute("select company, account, round(sum(value)/1000.0), period from financials where scenario = \'" + selected_scenario + "\' and version = 'vf' and account = \'" + selected_fsli + "\' and period <= \'" +end_date_str+ "\' group by company, period order by period;");
            for row in cursor.fetchall():
                af_value_list.append([str(row[0]),str(row[1]),row[2],date_utils.calc_forecast_monthly_headers(row[3].year, row[3].month)]);

        with connection.cursor() as cursor:
            cursor.execute("select company, account, round(sum(value)/1000.0), period from financials where scenario = '2017 August AMR Budget' and version = 'vf' and account = \'" + selected_fsli + "\' and period <= \'" + end_date_str + "\' group by company, period order by period;");
            for row in cursor.fetchall():
                budget_value_list.append([str(row[0]),str(row[1]),row[2],date_utils.calc_forecast_monthly_headers(row[3].year, row[3].month)]);
    else:
        with connection.cursor() as cursor:
            cursor.execute("select entity, account, round(sum(value)/1000.0), period from financials where entity = \'" + selected_entity + "\' and scenario = \'" + selected_scenario + "\' and version = 'vf' and account = \'" + selected_fsli + "\' and period <= \'" +end_date_str+ "\' group by entity, period order by period;");
            for row in cursor.fetchall():
                af_value_list.append([str(row[0]),str(row[1]),row[2],date_utils.calc_forecast_monthly_headers(row[3].year, row[3].month)]);

        with connection.cursor() as cursor:
            cursor.execute("select entity, account, round(sum(value)/1000.0), period from financials where entity = \'" + selected_entity + "\' and scenario = '2017 August AMR Budget' and version = 'vf' and account = \'" + selected_fsli + "\' and period <= \'" + end_date_str + "\' group by entity, period order by period;");
            for row in cursor.fetchall():
                budget_value_list.append([str(row[0]),str(row[1]),row[2],date_utils.calc_forecast_monthly_headers(row[3].year, row[3].month)]);

    if selected_entity == 'Summary':
        selected_entity = selected_company;


    for item in af_value_list:
        print (item);

    for item in budget_value_list:
        print (item);

    status = {"selected_entity":selected_entity, "selected_fsli": selected_fsli, "af_value_list":json.dumps(af_value_list), "budget_value_list":json.dumps(budget_value_list)};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;



def get_all_entity(company, scenario):
    entity_list = [];
    with connection.cursor() as cursor:
        cursor.execute("select distinct company, entity from financials where scenario = \'" + scenario + "\' and company = \'" + company + "\';");
        for row in cursor.fetchall():
            entity_list.append(row[1]);

    return entity_list;

@login_required(redirect_field_name='', login_url='/')
def load_amr(request):
    request.session.set_expiry(SESSION_EXPIRE_SECONDS);
    print ("we are here!!!!!!!!!!!!!!");

    financials_result_list = financials.objects.raw("SELECT * FROM financials WHERE scenario = '2017 June AMR' AND company = 'Lightstone' AND entity='Gavin' AND period <='2017-12-31' AND period >= '2017-01-31' ORDER BY entity, account, period");

    fsli_order_list = ['Energy Revenue','Delivered Fuel Expense','Net Emissions Expense','Variable O&M Expense',\
                       'Fixed Fuel','Gross Energy Margin','Hedge P&L','Net Energy Margin','Capacity Revenue',\
                       'Ancillary Services Revenue','Misc Income','Total Other Income','Gross Margin',\
                       'Labor Expenses','Maintenance','Operations','Removal Costs','Fuel Handling',\
                       'Fixed Non-Labor Expense','Property Tax','Insurance','General & Administrative','Total Fixed Costs',\
                       'EBITDA','Maintenance Capex','Environmental Capex','LTSA Capex','Growth Capex','Total Capex',\
                       'EBITDA less Capex'];

    existing_company_scenario_list = get_company_scenario_list();
    if not request.user.is_authenticated():
        return redirect('/login/');
    else:
        return render(request, 'amr.html', {'user_name':str(request.user), 'financials_result_list':financials_result_list, 'fsli_order_list':fsli_order_list, 'existing_company_scenario_list':existing_company_scenario_list, 'entity_list':entity_list});






@login_required(redirect_field_name='', login_url='/')
def pjm_api_call(request):
    selected_company = request.GET.get("company_entity");

    # company_name = entity_full.split(" ")[0];
    # entity_name = entity_full.split(" ")[1];

    start_date = request.GET.get("start_date");
    end_date = request.GET.get("end_date");
    dart = request.GET.get("dart");

    frequency = "daily";
    data_info = 'LMP/' + dart + "/" + frequency;
    date_range = start_date + " - " + end_date;

    print (selected_company, start_date, end_date, dart, frequency);

    """ this raw sql statement will be changed if in the future, each unit has differenct pnode id """
    # print ("SELECT * FROM power_plants WHERE company = \'" + selected_company + "\' group by power_plant_name");
    entity_list = power_plants.objects.raw("SELECT * FROM power_plants WHERE company = \'" + selected_company + "\' group by power_plant_name");

    pnode_list = [selected_entity.pnode_id for selected_entity in entity_list];

    if pnode_list == []:
        return render(request, 'sys_mainpage_pjmlmp.html', {"result_list": [], "user_name": str(request.user), "company":selected_company, "entity_str":'' ,"date_range":date_range, "data_info": data_info});


    entity_str_list = [selected_entity.power_plant_name for selected_entity in entity_list];

    entity_str = ','.join(entity_str_list);

    print (pnode_list);


    url = 'https://dataminer.pjm.com/dataminer/rest/public/api/markets/' + dart + '/lmp/' + frequency;


    try:

        data_flag = False;
        tried_times = 10;
        result_list = [];
        info_list = [];
        data = {"startDate": start_date, "endDate": end_date, "pnodeList": pnode_list}
        data = json.dumps(data)

        # url = 'https://dataminer.pjm.com/dataminer/rest/public/api/markets/realtime/lmp/daily'
        # url = 'https://dataminer.pjm.com/dataminer/rest/public/api/markets/dayahead/lmp/daily'
        headers = {'Content-Type': 'application/json'}

        while not data_flag and tried_times > 0:
            try:
                print (tried_times);

                response = requests.post(url, data=data, headers=headers)

                print(response.status_code)
                result_json = response.json();

                for item in result_json:
                    # print (item)
                    pnode_id = item['pnodeId'];
                    publish_date = item['publishDate'];
                    price_type = item['priceType'];
                    company_name = selected_company;
                    entity_name = [selected_entity.power_plant_name for selected_entity in entity_list if selected_entity.pnode_id == str(pnode_id)][0];
                    for item_i in item:
                        if item_i == 'prices':
                            for price in item[item_i]:
                                result_list.append([company_name, entity_name, pnode_id, publish_date, dart ,price_type, price['utchour'], price['price']]);
                data_flag = True;
            except:
                data_flag = False;
                tried_times -= 1;


        latest_lmp_info_list = [];
        with connection.cursor() as cursor:
            cursor.execute("select b.company, b.power_plant_name, b.pnode_id, a.valuation_date, a.dart from kean.lmp a join kean.power_plants b on a.pnode_id = b.pnode_id where a.valuation_date = (select max(valuation_date) from kean.lmp) group by a.pnode_id, a.dart;");
            for row in cursor.fetchall():
                    latest_lmp_info_list.append([row[0],row[1],row[2],str(row[3]),row[4]]);

        return render(request, 'sys_mainpage_pjmlmp.html', {"result_list": result_list, "user_name": str(request.user), "company":selected_company, "entity_str":entity_str ,"date_range":date_range, "data_info": data_info, 'latest_lmp_info_list':latest_lmp_info_list});
    except:
        result_list = ['Please try again.'];
        return render(request, 'sys_mainpage_pjmlmp.html', {"result_list": result_list, "user_name": str(request.user)});



@csrf_exempt
@login_required(redirect_field_name='', login_url='/')
def upload_pjmlmp_to_kean(request):
    lmp_result_list = json.loads(request.POST.get("lmp_result_list"));
    dart = request.POST.get("dart");
    # print (len(lmp_result_list));
    # for item in lmp_result_list:
    #     print (item);

    # """ extremaly pythonic """
    # company_entity_pair_list = list(set(list(zip(*list(list(zip(*lmp_result_list))[0:2])))));
    lmp_result_df = pd.DataFrame(data = lmp_result_list, columns = ['company','entity','pnode','publish_time','dart','type','period_time','value']);

    print (len(lmp_result_df));


    lmp_ready_to_kean_list = [];

    grouped_lmp_result_df = lmp_result_df.groupby(['pnode']);

    for pnode_id in grouped_lmp_result_df.groups:
        current_lmp_result_df = grouped_lmp_result_df.get_group(pnode_id);
        cong_lmp_df = current_lmp_result_df.loc[current_lmp_result_df['type'] == 'CongLMP'];
        cong_lmp_df.sort_values('period_time');

        utc_time_str_list = list(cong_lmp_df['period_time']);
        date_hour_ending_list = get_date_hour_ending(utc_time_str_list);

        dart_list = list(cong_lmp_df['dart']);

        dart_converted_list = [];
        for item in dart_list:
            converted_dart ='Day Ahead' if item == 'dayahead' else 'Real Time';
            dart_converted_list.append(converted_dart);

        cong_lmp_prices_list = list(cong_lmp_df['value']);

        loss_lmp_df = current_lmp_result_df.loc[current_lmp_result_df['type'] == 'LossLMP'];
        loss_lmp_df.sort_values('period_time');

        loss_lmp_prices_list = list(loss_lmp_df['value']);

        total_lmp_df = current_lmp_result_df.loc[current_lmp_result_df['type'] == 'TotalLMP'];
        total_lmp_df.sort_values('period_time');

        total_lmp_prices_list = list(total_lmp_df['value']);

        pnode_id_list = [pnode_id for i in range(0, len(date_hour_ending_list))];

        temp_ready_list = [list(zip(*date_hour_ending_list))[0], pnode_id_list, dart_converted_list, list(zip(*date_hour_ending_list))[1], total_lmp_prices_list, cong_lmp_prices_list, loss_lmp_prices_list];

        temp_ready_list = list(zip(*temp_ready_list));

        lmp_ready_to_kean_list += temp_ready_list;


    filter_valuation_date_list = list(set(list(zip(*lmp_ready_to_kean_list))[0]));
    filter_pnode_list = list(set(list(zip(*lmp_ready_to_kean_list))[1]));
    filter_dart_list = list(set(list(zip(*lmp_ready_to_kean_list))[2]));

    # print (filter_valuation_date_list);
    # print (filter_pnode_list);
    # print (filter_dart_list);

    lmp.objects.filter(valuation_date__in=filter_valuation_date_list, pnode_id__in=filter_pnode_list, dart__in=filter_dart_list).delete();

    lmp_ready_to_kean_objs_list = [];

    # item = lmp_ready_to_kean_list[0];
    #
    # lmp_obj = lmp(valuation_date=item[0],pnode_id=item[1],dart=item[2],
    #                                        hour_ending=item[3],total_lmp=item[4],congestion_price=item[5],
    #                                        marginal_loss_price=item[6]);

    # lmp_obj.save();


    for item in lmp_ready_to_kean_list:
        lmp_ready_to_kean_objs_list.append(lmp(valuation_date=item[0],pnode_id=item[1],dart=item[2],
                                           hour_ending=item[3],total_lmp=item[4],congestion_price=item[5],
                                           marginal_loss_price=item[6]));


    lmp.objects.bulk_create(lmp_ready_to_kean_objs_list);

    latest_lmp_info_list = [];
    with connection.cursor() as cursor:
        cursor.execute("select b.company, b.power_plant_name, b.pnode_id, a.valuation_date, a.dart from kean.lmp a join kean.power_plants b on a.pnode_id = b.pnode_id where a.valuation_date = (select max(valuation_date) from kean.lmp) group by a.pnode_id, a.dart;");
        for row in cursor.fetchall():
            latest_lmp_info_list.append([row[0],row[1],row[2],str(row[3]),row[4]]);

    status = {"latest_lmp_info_list":latest_lmp_info_list};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;



DAYLIGHT_SAV_SUMMER = ['2016-03-13','2017-03-12','2018-03-11','2019-03-10','2020-03-08','2021-03-14','2022-03-13'];
DAYLIGHT_SAV_WINTER = ['2016-11-06','2017-11-05','2018-11-04','2019-11-03','2020-11-01','2021-11-07','2022-11-06'];


def get_date_hour_ending(utc_time_str_list):
    start_hour_ending = 1;
    date_hour_ending_list = [];

    current_date = get_valuation_date(utc_time_str_list[0]);


    for i in range(0, len(utc_time_str_list)):
        check_count = 25;

        if current_date in DAYLIGHT_SAV_WINTER:
            check_count = 26
        if current_date in DAYLIGHT_SAV_SUMMER:
            check_count = 24;

        if i == 0:
            date_hour_ending_list.append([get_valuation_date(utc_time_str_list[i]), str(start_hour_ending)+'00' if len(str(start_hour_ending)) == 2 else '0' + str(start_hour_ending)+'00']);
            start_hour_ending += 1;
            current_date = get_valuation_date(utc_time_str_list[i]);
        else:
            if int(get_time(utc_time_str_list[i])[0:2]) - int(get_time(utc_time_str_list[i-1])[0:2]) == 1:
                date_hour_ending_list.append([current_date, str(start_hour_ending)+'00' if len(str(start_hour_ending)) == 2 else '0' + str(start_hour_ending)+'00']);
                start_hour_ending += 1;
            if int(get_time(utc_time_str_list[i])[0:2]) - int(get_time(utc_time_str_list[i-1])[0:2]) == -23:
                date_hour_ending_list.append([current_date, str(start_hour_ending)+'00' if len(str(start_hour_ending)) == 2 else '0' + str(start_hour_ending)+'00']);
                start_hour_ending += 1;

            if start_hour_ending == check_count:
                # print ("herehere");
                start_hour_ending = 1;
                current_date = get_valuation_date(utc_time_str_list[i]);


    # for item in date_hour_ending_list:
    #     print (item);

    return date_hour_ending_list;





def get_valuation_date(utc_time_str):
    return utc_time_str.split("T")[0];

def get_time(utc_time_str):
    return utc_time_str.split("T")[1];



@csrf_exempt
@login_required(redirect_field_name='', login_url='/')
def run_amr(request):
    amr_switch_list = json.loads(request.POST.get("amr_run_selection_list"));
    # amr_uselastvf_list = json.loads(request.POST.get("amr_uselastvf_selection_list"));
    print (type(amr_switch_list));
    # print("herehere: ",amr_uselastvf_list);


    selected_company_scenario = request.POST.get("selected_com_scen");
    selected_budget_scenario = request.POST.get("budget_scenario");




    selected_company = selected_company_scenario.split("-")[0];
    selected_amr_scenario = selected_company_scenario.split("-")[1];

    print (amr_switch_list, selected_company_scenario, selected_budget_scenario);

    for item in amr_switch_list:
        print (item);
        if item == 'dispatch':
            test_run.kean_proj_run_dispatch(selected_company, selected_amr_scenario);
        if item == 'actuals':
            test_run.kean_proj_run_actuals(selected_company, selected_amr_scenario);
        if item == 'hedge':
            test_run.kean_proj_run_hedge(selected_amr_scenario, selected_company);
        if item == 'respreads':
            test_run.kean_proj_run_respreads(selected_company, selected_amr_scenario, selected_budget_scenario);
        if item == 'labor':
            test_run.kean_proj_run_labor(selected_amr_scenario, selected_company);






    status = {"latest_lmp_info_list":[]};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;





@login_required(redirect_field_name='', login_url='/')
def checkview(request):
    existing_company_scenario_list = get_company_scenario_list();


    return render(request, 'sys_mainpage_checkview.html',{'user_name':str(request.user),'existing_company_scenario_list':existing_company_scenario_list});



@login_required(redirect_field_name='', login_url='/')
def calc_control(request):
    existing_company_scenario_list = get_company_scenario_list();

    selected_company = existing_company_scenario_list[0].split("-")[0];
    selected_scenario = existing_company_scenario_list[0].split("-")[1];



    latest_budget_scenario_list = get_latest_budget_scenario(selected_company);

    status_count = get_current_amr_budget_status(selected_company, selected_scenario);
    budget_status_count = get_current_budget_status(selected_company, latest_budget_scenario_list[-1]);



    return render(request, 'sys_mainpage_calc_control.html',{'user_name':str(request.user),'existing_company_scenario_list':existing_company_scenario_list, 'latest_budget_scenario_list':latest_budget_scenario_list,'status_count':status_count, "budget_status_count":budget_status_count});


@login_required(redirect_field_name='', login_url='/')
def copy_from_selected(request,current_com_scen, selected_com_scen, fsli, module):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];
    current_scenario = current_com_scen.split("-")[1];

    print (selected_company, selected_scenario, fsli, module);

    test_run.kean_proj_copy_from_selected(selected_company, current_scenario, selected_scenario, fsli, module);








# last_amr_scenario = date_utils.get_last_amr_scenario(scenario);
#
# last_amr_fsli_list = get_amr_fsli_list(selected_company, last_amr_scenario);

# def get_amr_fsli_list(company, scenario):
#
#     print ("we want to get fsli list:", company, scenario);
#
#     fsli_list = [];
#
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT distinct account from financials WHERE company = \'" + company + "\' AND scenario = \'" + last_amr_scenario + "\' AND version = 'vf';");
#
#         for row in cursor.fetchall():
#             fsli_list.append(row[0]);
#
#     for item in fsli_list:
#         print (item);
#
#     return fsli_list;







@login_required(redirect_field_name='', login_url='/')
def run_budget(request, selected_com_scen, budget_scenario):
    print (selected_com_scen);
    print (budget_scenario);



    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];
    test_run.kean_proj_run_budget(selected_company, selected_scenario, budget_scenario);

    status_count = get_current_amr_budget_status(selected_company, selected_scenario);
    budget_status_count = get_current_budget_status(selected_company, budget_scenario);


    status = {"selected_company_scenario" : selected_com_scen, "budget_scenario":budget_scenario, "status_count":status_count, "budget_status_count":budget_status_count};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);

    return response;

@login_required(redirect_field_name='', login_url='/')
def run_budget_for_forecast_period(request, selected_com_scen, budget_scenario):
    print (selected_com_scen);
    print (budget_scenario);



    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];
    test_run.kean_proj_run_budget_for_forecast_period(selected_company, selected_scenario, budget_scenario);

    status_count = get_current_amr_budget_status(selected_company, selected_scenario);
    budget_status_count = get_current_budget_status(selected_company, budget_scenario);

    status = {"selected_company_scenario" : selected_com_scen, "budget_scenario":budget_scenario, "status_count":status_count, "budget_status_count":budget_status_count};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);

    return response;



@login_required(redirect_field_name='', login_url='/')
def make_version(request, selected_com_scen, input_version):
    print (selected_com_scen, input_version);
    if input_version == 'Current':
        input_version = '';

    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];

    test_run.kean_proj_make_version(selected_scenario, selected_company, input_version,False);






@login_required(redirect_field_name='', login_url='/')
def run_pxq(request, selected_com_scen, amr_version, budget_scenario):
    print (selected_com_scen, amr_version);
    selected_company = selected_com_scen.split('-')[0];
    selected_scenario = selected_com_scen.split('-')[1];

    if 'Current' in amr_version:
        amr_version = '';

    download_report_file_path = test_run.kean_proj_run_pxq(selected_company, selected_scenario, amr_version, budget_scenario);


    file_name = r"/".join(download_report_file_path.split(r"/")[-4:]);

    print (file_name);

    status = {"file_path" : file_name};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;









@login_required(redirect_field_name='', login_url='/')
def run_liquidity(request, selected_com_scen, amr_version):
    print (selected_com_scen, amr_version);
    selected_company = selected_com_scen.split('-')[0];
    selected_scenario = selected_com_scen.split('-')[1];

    if 'Current' in amr_version:
        amr_version = '';


    """
        for valuation data, we should go to the database and query out the first valuation date for the selected scenario
    """


    valuation_date_dict = {"2017 July AMR":date(2017,7,27), "2017 August AMR":date(2017,8,29)};

    valuation_date = valuation_date_dict[selected_scenario];

    liquidity_report_file_path, debt_balance_report_file_path, interest_expense_report_file_path, est_tax_dist_report_file_path = test_run.kean_proj_run_liquidity(selected_scenario, selected_company, amr_version, valuation_date=valuation_date);

    liquidity_report_file_path = liquidity_report_file_path.split(r"/")[-1:];
    debt_balance_report_file_path = debt_balance_report_file_path.split(r"/")[-1:];
    interest_expense_report_file_path = interest_expense_report_file_path.split(r"/")[-1:];
    est_tax_dist_report_file_path = est_tax_dist_report_file_path.split(r"/")[-1:];



    status = {"liquidity_file_path" : liquidity_report_file_path, "debt_balance_file_path":debt_balance_report_file_path, "interest_expense_file_path":interest_expense_report_file_path, "est_tax_dist_file_path":est_tax_dist_report_file_path};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;


""" To be implemented """
# def get_valuation_date(scenario, company):
#     with connection.cursor() as cursor:
#         cursor.execute("");
#
#         for row in cursor.fetchall():
#             count = int(row[0])



def get_current_amr_budget_status(company, scenario):
    count = 0;

    forecast_year_list = list(range(int(scenario.split(" ")[0]), int(scenario.split(" ")[0])+5));

    forecast_year_start = forecast_year_list[1];
    forecast_year_end = forecast_year_list[-1];

    forecast_date_start = str(forecast_year_start) + "-01-01";
    forecast_date_end = str(forecast_year_end) + "-12-31";

    print (forecast_date_start, forecast_date_end);

    with connection.cursor() as cursor:
        cursor.execute("select count(*) from financials where company = \'" + company + "\' and scenario = \'" + scenario + "\' and version = '' and period >= \'" + forecast_date_start + "\'\
                                    and period <= \'" + forecast_date_end + "\' \
                                    and account in ('Maintenance','Operations','Removal Costs','Fuel Handling','Fixed Non-Labor Expense','Property Tax',\
    												'Insurance', 'General & Administrative', 'Total Fixed Costs', 'EBITDA', 'Maintenance Capex',\
    												'Environmental Capex','LTSA Capex','Growth Capex');");

        for row in cursor.fetchall():
            count = int(row[0])

    return count;


def get_current_budget_status(company, scenario):
    count = 0;

    forecast_year_list = list(range(int(scenario.split(" ")[0]), int(scenario.split(" ")[0])+5));

    forecast_year_start = forecast_year_list[1];
    forecast_year_end = forecast_year_list[-1];

    forecast_date_start = str(forecast_year_start) + "-01-01";
    forecast_date_end = str(forecast_year_end) + "-12-31";

    print (forecast_date_start, forecast_date_end);

    with connection.cursor() as cursor:
        cursor.execute("select count(*) from financials where company = \'" + company + "\' and scenario = \'" + scenario + "\' and version = 'vf';");
        for row in cursor.fetchall():
            count = int(row[0])

    return count;


def get_latest_budget_scenario(company):
    budget_scenario_list = [];
    with connection.cursor() as cursor:
        cursor.execute("select distinct scenario from budget where company = \'" + company + "\'");
        for row in cursor.fetchall():
            budget_scenario_list.append(row[0]);

    return budget_scenario_list;





def get_company_scenario_list():
    existing_company_scenario_list = [];
    with connection.cursor() as cursor:
        cursor.execute("select distinct company,scenario from company_scenario order by id_company_scenario desc, scenario asc;");
        for row in cursor.fetchall():
            # print (row[0],row[1]);
            existing_company_scenario_list.append(str(row[0])+"-"+str(row[1]));

    return existing_company_scenario_list;


def check_financials_status(request, selected_com_scen):
    print ("----------------------------------------------------");
    print (selected_com_scen);
    print ("----------------------------------------------------");

    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];

    version_list = get_financials_status_by_company_scenario(selected_company, selected_scenario);

    input_status_list = get_input_status(selected_company, selected_scenario);

    actuals_period = '';
    forecast_period = '';

    actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list = get_dates_info_from_amr_scenario(selected_scenario);

    actuals_period = actuals_month_dates_list[0] + " thru " + actuals_month_dates_list[-1];

    estimate_period = estimate_month_dates_list[0] + " thru " + estimate_month_dates_list[-1];

    forecast_period = str(int(actuals_month_dates_list[0].split("-")[0]) + 1) + "-01-31" + " thru " + str(int(actuals_month_dates_list[0].split("-")[0]) + 4) + "-12-31";

    print (selected_company, "     ", selected_scenario);

    status = {"selected_company_scenario" : selected_com_scen, "version_list":version_list, "actuals_period":actuals_period, "estimate_period":estimate_period, "forecast_period":forecast_period, "input_status_list":input_status_list};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;


def get_input_status(selected_company, selected_scenario):
    input_status_list = [];
    with connection.cursor() as cursor:
        cursor.execute("select entity,min(accounting_month), max(accounting_month), count(*) from actuals where company = \'" + selected_company + "\' AND scenario = \'" + selected_scenario + "\' group by entity");

        check_flag = 0;

        for row in cursor.fetchall():
            check_flag = 1;
            period_range = str(row[1]) + " thru " + str(row[2]);
            input_status_list.append(['Actuals', row[0], period_range, row[3]]);

        if check_flag == 0:
            input_status_list.append(['Actuals', 'N/A', 'N/A', 'No Input in KEAN']);



    with connection.cursor() as cursor:
        cursor.execute("select entity,min(period), max(period), count(*) from budget where company = \'" + selected_company + "\' AND scenario = '2017 June AMR Budget' group by entity");

        check_flag = 0;

        for row in cursor.fetchall():
            check_flag = 1;
            period_range = str(row[1]) + " thru " + str(row[2]);
            input_status_list.append(['Budget', row[0], period_range, row[3]]);

        if check_flag == 0:
            input_status_list.append(['Budget', 'N/A', 'N/A', 'No Input in KEAN']);


    with connection.cursor() as cursor:
        cursor.execute("select entity,min(period), max(period), count(*) from dispatch where company = \'" + selected_company + "\' AND scenario = \'" + selected_scenario + "\' group by entity");

        check_flag = 0;

        for row in cursor.fetchall():
            check_flag = 1;
            period_range = str(row[1]) + " thru " + str(row[2]);
            input_status_list.append(['Dispatch', row[0], period_range, row[3]]);

        if check_flag == 0:
            input_status_list.append(['Dispatch', 'N/A', 'N/A', 'No Input in KEAN']);

    with connection.cursor() as cursor:
        cursor.execute("select entity,min(period), max(period), count(*) from project_respread where company = \'" + selected_company + "\' AND scenario = \'" + selected_scenario + "\' group by entity");

        check_flag = 0;

        for row in cursor.fetchall():
            check_flag = 1;
            period_range = str(row[1]) + " thru " + str(row[2]);
            input_status_list.append(['Project Respreads', row[0], period_range, row[3]]);

        if check_flag == 0:
            input_status_list.append(['Project Respreads', 'N/A', 'N/A', 'No Input in KEAN']);



    return input_status_list;




def get_financials_status_by_company_scenario(selected_company, selected_scenario):
    raw_query_str = "select distinct version from financials where company = \'" +selected_company+ "\' AND scenario = \'" +selected_scenario+ "\' order by version desc";
    version_list_for_selected = [];
    with connection.cursor() as cursor:
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            if row[0] =='':
                version_list_for_selected.append("Current Developing");
            else:
                version_list_for_selected.append(row[0]);
    return version_list_for_selected;

def get_month_dates_list(year, start_month, end_month):
    month_dates_list = [];
    for month in range(start_month, end_month+1):
        month_str = str(month) if len(str(month)) > 1 else "0"+str(month);
        date_str = str(year) + "-" + month_str + "-" + str(calendar.monthrange(year, month)[1]);
        month_dates_list.append(date_str);
    return month_dates_list;

def get_dates_info_from_amr_scenario(amr_scenario):
    year = int(amr_scenario.split(" ")[0]);
    end_month = MONTH_NUMBER_DICT[amr_scenario.split(" ")[1]];

    start_month = 1;
    last_month = 12;

    actuals_month_dates_list = get_month_dates_list(year, start_month, end_month);
    budget_month_dates_list = get_month_dates_list(year, start_month, last_month);
    estimate_month_dates_list = get_month_dates_list(year, end_month+1, last_month);

    return actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list;



LIGHTSTONE_FSLI_INFO_MAPPING_EST = {'Hedge P&L':'hedge individual',
                                'Capacity Revenue':'capacity individual',
                                'Fixed Fuel':'dispatch',
                                'Misc Income':'direct upload',
                                'Ancillary Services Revenue':'direct upload',
                                'Fuel Handling':'respreads',
                                'Insurance':'direct upload',
                                'Environmental Capex':'respreads',
                                'Property Tax':'direct upload',
                                'Maintenance':'respreads',
                                'LTSA Capex':'direct upload',
                                'Operations':'respreads',
                                'Maintenance Capex':'respreads',
                                'Growth Capex':'respreads',
                                'Removal Costs':'respreads',
                                'Labor Expenses':'labor individual',
                                'General & Administrative':'respreads',
                                'Energy Revenue':'dispatch',
                                'Delivered Fuel Expense':'dispatch',
                                'Net Emissions Expense':'dispatch',
                                'Variable O&M Expense':'dispatch'}


LIGHTSTONE_FSLI_INFO_MAPPING_BUD = {'Hedge P&L':'hedge individual',
                                'Capacity Revenue':'capacity individual',
                                'Fixed Fuel':'dispatch',
                                'Misc Income':'direct upload',
                                'Ancillary Services Revenue':'direct upload',
                                'Fuel Handling':'budget',
                                'Insurance':'direct upload',
                                'Environmental Capex':'budget',
                                'Property Tax':'direct upload',
                                'Maintenance':'budget',
                                'LTSA Capex':'direct upload',
                                'Operations':'budget',
                                'Maintenance Capex':'budget',
                                'Growth Capex':'budget',
                                'Removal Costs':'budget',
                                'Labor Expenses':'labor individual',
                                'General & Administrative':'budget',
                                'Energy Revenue':'dispatch',
                                'Delivered Fuel Expense':'dispatch',
                                'Net Emissions Expense':'dispatch',
                                'Variable O&M Expense':'dispatch'}

def check_version_status(request, selected_com_scen, selected_version):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];


    actuals_split_date = '';

    if 'AMR' in selected_com_scen:
        actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list = get_dates_info_from_amr_scenario(selected_scenario);

        actuals_split_date = actuals_month_dates_list[-1];
    else:
        actuals_split_date = '2050-12-31';


    actuals_month_dates_list, budget_month_dates_list, estimate_month_dates_list = get_dates_info_from_amr_scenario(selected_scenario);

    actuals_period = actuals_month_dates_list[0] + " thru " + actuals_month_dates_list[-1];

    estimate_period = estimate_month_dates_list[0] + " thru " + estimate_month_dates_list[-1];

    forecast_period = str(int(actuals_month_dates_list[0].split("-")[0]) + 1) + "-01-31 " + "thru " + str(int(actuals_month_dates_list[0].split("-")[0]) + 4) + "-12-31";


    if selected_version == 'Current':
        selected_version = '';


    if 'Budget' in selected_scenario:
        raw_query_str = "select entity, account, count(*), min(period), max(period) , sum(value)  from financials where company = \'" + selected_company + "\' and scenario = \'" + selected_scenario + "\' and version = \'" \
                        + selected_version + "\' group by entity, account order by entity, account;";

        fsli_status_list = [];
        with connection.cursor() as cursor:
            cursor.execute(raw_query_str);
            for row in cursor.fetchall():
                module = 'calcs';
                if row[1] in LIGHTSTONE_FSLI_INFO_MAPPING_EST:
                    module = 'budget';
                period_range = str(row[3]) + " thru " + str(row[4]);
                fsli_status_list.append([row[0],row[1],period_range, module,row[2], row[5]]);

    else:

        raw_query_str = "select entity, account, count(*), min(period), max(period) , sum(value)  from financials where company = \'" + selected_company + "\' and scenario = \'" + selected_scenario + "\' and version = \'" \
                        + selected_version + "\' and period >= \'" + estimate_month_dates_list[0] + "\' and period <= \'" + estimate_month_dates_list[-1] + "\' group by entity, account order by entity, account;";


        fsli_status_list = [];
        with connection.cursor() as cursor:
            cursor.execute(raw_query_str);
            for row in cursor.fetchall():
                module = 'calcs';
                if row[1] in LIGHTSTONE_FSLI_INFO_MAPPING_EST:
                    module = LIGHTSTONE_FSLI_INFO_MAPPING_EST[row[1]];

                period_range = str(row[3]) + " thru " + str(row[4]);
                fsli_status_list.append([row[0],row[1],period_range, module,row[2], row[5]]);


        raw_query_str = "select entity, account, count(*), min(period), max(period), sum(value)  from financials where company = \'" + selected_company + "\' and scenario = \'" + selected_scenario + "\' and version = \'" \
                        + selected_version + "\' and period >= \'" + actuals_month_dates_list[0] + "\' and period <= \'" + actuals_month_dates_list[-1] + "\' group by entity, account order by entity, account;";


        with connection.cursor() as cursor:
            cursor.execute(raw_query_str);
            for row in cursor.fetchall():
                module = 'calcs';
                if row[1] in LIGHTSTONE_FSLI_INFO_MAPPING_EST:
                    module = 'actuals/accounting';

                period_range = str(row[3]) + " thru " + str(row[4]);
                fsli_status_list.append([row[0],row[1],period_range, module,row[2], row[5]]);


        raw_query_str = "select entity, account, count(*), min(period), max(period), sum(value)  from financials where company = \'" + selected_company + "\' and scenario = \'" + selected_scenario + "\' and version = \'" \
                        + selected_version + "\' and period >= \'" + str(int(actuals_month_dates_list[0].split("-")[0]) + 1) + "-01-31" + "\' and period <= \'" + str(int(actuals_month_dates_list[0].split("-")[0]) + 4) + "-12-31" + "\' group by entity, account order by entity, account;";


        with connection.cursor() as cursor:
            cursor.execute(raw_query_str);
            for row in cursor.fetchall():
                module = 'calcs';
                if row[1] in LIGHTSTONE_FSLI_INFO_MAPPING_BUD:
                    module = LIGHTSTONE_FSLI_INFO_MAPPING_BUD[row[1]];


                period_range = str(row[3]) + " thru " + str(row[4]);
                fsli_status_list.append([row[0],row[1],period_range, module,row[2], row[5]]);


    fsli_status_list = sorted(fsli_status_list, key = lambda x: (x[0],x[1]));

    status = {"fsli_status_list" : fsli_status_list};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;



@login_required(redirect_field_name='', login_url='/')
def initiate_amr(request, new_com_scen):
    existing_company_scenario_list = [];
    print (new_com_scen);
    company = new_com_scen.split("-")[0];
    scenario = new_com_scen.split("-")[1];

    company_scenario.objects.create(company = company, scenario = scenario);



    existing_company_scenario_list = get_company_scenario_list();

    return render(request, 'sys_mainpage_checkview.html',{'user_name':str(request.user),'existing_company_scenario_list':existing_company_scenario_list});


@login_required(redirect_field_name='', login_url='/')
def data_prepare(request):
    existing_company_scenario_list = get_company_scenario_list();
    return render(request, 'sys_mainpage_data_input.html',{'user_name':str(request.user), 'existing_company_scenario_list':existing_company_scenario_list});


@login_required(redirect_field_name='', login_url='/')
def run_amr_report(request):
    existing_company_scenario_list = get_company_scenario_list();
    existing_company_list = get_company_list();

    return render(request, 'sys_mainpage_report.html',{'user_name':str(request.user), 'existing_company_scenario_list':existing_company_scenario_list, 'existing_company_list':existing_company_list});


def get_company_list():

    raw_query_str = "SELECT DISTINCT company from financials";

    company_list = [];

    with connection.cursor() as cursor:
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            if row[0] != '':
                company_list.append(row[0]);

    return company_list;




@login_required(redirect_field_name='', login_url='/')
def check_company_status(request, selected_company):
    raw_query_str = "SELECT DISTINCT scenario, version, year(period) from financials where company=\'" + selected_company + "\';";

    company_status_list = [];

    with connection.cursor() as cursor:
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            current_scenario = row[0];
            current_version = row[1] if row[1] != '' else 'Current Developing';
            current_year = str(row[2]);
            company_status_list.append(current_scenario + "-" + current_version + "-" + current_year);

    status = {"company_status_list" : company_status_list};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;




@login_required(redirect_field_name='', login_url='/')
def initiate_amr_report(request, selected_com_scen):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];


    raw_query_str = "SELECT distinct version from financials WHERE company = \'" + selected_company + "\' AND scenario = \'" + selected_scenario + "\'";

    amr_version_list = [];
    with connection.cursor() as cursor:
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            if row[0] == '':
                amr_version_list.append('Current Developing');
            else:
                amr_version_list.append(row[0]);


    print (len(amr_version_list));

    latest_budget_scenario_list = get_latest_budget_scenario(selected_company);

    print ("latest_budget_scenario_list:", latest_budget_scenario_list);


    version_year_list = get_version_year_list(selected_company, selected_scenario);


    status = {"version_list" : amr_version_list,"latest_budget_scenario_list":latest_budget_scenario_list, "version_year_list":version_year_list};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;


def get_version_year_list(company, scenario):
    version_year_list = [];
    with connection.cursor() as cursor:
        raw_query_str = "select distinct version, year(period) from financials where company = \'" + company + "\' and scenario = \'" + scenario + "\'; "
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            if row[0] == '':
                version_year_list.append('Current Developing-'+str(row[1]));
            else:
                version_year_list.append(row[0]+"-"+str(row[1]));
    return version_year_list;



@login_required(redirect_field_name='', login_url='/')
def generate_amr_report(request, selected_com_scen, amr_version, budget_scenario):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];


    if 'Current' in amr_version:
        amr_version = '';

    # print ("???????????????????????????????????????????????",amr_version);


    download_report_file_path = test_run.kean_proj_run_amr_report(selected_company, selected_scenario, amr_version, budget_scenario)

    # print (download_report_file_path);

    file_name = download_report_file_path.split(r"/")[-1];


    status = {"file_path" : file_name};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;



@login_required(redirect_field_name='', login_url='/')
def generate_diff_report(request, first_svy, second_svy, selected_company):

    print (first_svy);
    print (second_svy);

    first_scenario = first_svy.split("-")[0];
    first_version = first_svy.split("-")[1];
    if 'Current' in first_version:
        first_version = '';
    first_year = int(first_svy.split("-")[2]);

    second_scenario = second_svy.split("-")[0];
    second_version = second_svy.split("-")[1];
    if 'Current' in second_version:
        second_version = '';

    second_year = int(second_svy.split("-")[2]);


    download_report_file_path = test_run.kean_proj_run_diff_report(selected_company, first_scenario, second_scenario, first_year, second_year , first_version, second_version);

    print (download_report_file_path);

    file_name = download_report_file_path.split(r"/")[-1];


    status = {"file_path" : file_name};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;


@login_required(redirect_field_name='', login_url='/')
def generate_variance_report(request, selected_com_scen, amr_version, budget_scenario):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];

    if 'Current' in amr_version:
        amr_version = '';

    download_report_file_path_ytd, download_report_file_path_mtd = test_run.kean_proj_run_variance_report(selected_company, selected_scenario, amr_version, budget_scenario)


    file_name_ytd = download_report_file_path_ytd.split(r"/")[-1];
    file_name_mtd = download_report_file_path_mtd.split(r"/")[-1];

    status = {"file_path_ytd":file_name_ytd, "file_path_mtd":file_name_mtd};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;




@login_required(redirect_field_name='', login_url='/')
def generate_fy_report(request, selected_com_scen, version_year):
    selected_company = selected_com_scen.split("-")[0];
    selected_scenario = selected_com_scen.split("-")[1];

    selected_version = version_year.split("-")[0];
    selected_year = int(version_year.split("-")[1]);

    if 'Current' in selected_version:
        selected_version = '';

    # print ("???????????????????????????????????????????????",amr_version);

    print (selected_company, selected_scenario, selected_version, selected_year);

    download_report_file_path = test_run.kean_proj_run_fy_report(selected_company, selected_scenario, selected_version, selected_year)

    print (download_report_file_path);

    file_name = download_report_file_path.split(r"/")[-1];


    status = {"file_path" : file_name};
    data_json = json.dumps(status);
    response = HttpResponse();
    response['Content-Type'] = "text/javascript";
    response.write(data_json);
    return response;








@login_required(redirect_field_name='', login_url='/')
def upload_input_data(request):
    saved_file_path = '';
    if request.method == 'POST' and request.FILES['upload_file']:
        selected_module = request.POST.get('module_name');
        selected_com_scen = request.POST.get("com_scen_picker_upload");

        # print (selected_module);

        print (selected_com_scen);

        xlsx_file_name = selected_module + "_" + selected_com_scen.split("-")[0] + "_" + selected_com_scen.split("-")[1] + '.xlsx'
        saved_file_path = 'data/' + selected_module + r'/' + xlsx_file_name;

        exist_file_path = os.path.join(settings.MEDIA_ROOT, saved_file_path);

        for temp_file in os.listdir(os.path.join(settings.MEDIA_ROOT,'')):
            print (temp_file);


        print ("exist_file_path:    ",exist_file_path);
        if os.path.exists(exist_file_path):
            os.remove(exist_file_path);
        myfile = request.FILES['upload_file'];
        fs = FileSystemStorage();


        print (selected_com_scen);



        filename = fs.save(saved_file_path, myfile);
        uploaded_file_url = fs.url(filename);

        print (uploaded_file_url);

    file_uploaded_info = '';
    if saved_file_path != '':
        file_uploaded_info = saved_file_path + " uploaded to KEAN.";





    company = selected_com_scen.split("-")[0];
    scenario = selected_com_scen.split("-")[1];






    if selected_module == 'actuals':
        total_actuals_upload_list =  web_actuals_uploader.upload_actuals(myfile, company, scenario);
        upload_actuals_to_kean(total_actuals_upload_list, company, scenario);

    if selected_module == 'budget':
        budget_scenario = scenario + ' Budget';
        total_budget_upload_list =  web_budget_uploader.upload_budget(exist_file_path, company, budget_scenario);
        upload_budget_to_kean(total_budget_upload_list, company, budget_scenario);

    if selected_module == 'dispatch':
        total_dispatch_upload_list =  web_dispatch_uploader.upload_dispatch(exist_file_path, company, scenario);
        upload_dispatch_to_kean(total_dispatch_upload_list, company, scenario);

    if selected_module == 'respreads':
        total_respreads_upload_list =  web_respreads_uploader.upload_respreads(exist_file_path, company, scenario);
        upload_respreads_to_kean(total_respreads_upload_list, company, scenario);

    if selected_module == 'prices':
        total_prices_upload_list =  web_prices_uploader.upload_prices(exist_file_path, company, scenario);
        upload_prices_to_kean(total_prices_upload_list, company, scenario);

    if selected_module == 'labor':
        web_other_uploader.labor_data_upload(exist_file_path, company, scenario);

    if selected_module == 'manual':
        web_other_uploader.manual_data_upload(exist_file_path, company, scenario);

    if selected_module == 'pxq':
        print (company, scenario);
        pxq_input_data_list =  web_other_uploader.support_pxq_data_upload(exist_file_path, company, scenario);
        # print (len(pxq_input_data_list));
        upload_pxq_input_to_kean(pxq_input_data_list, company, scenario);







    existing_company_scenario_list = get_company_scenario_list();

    return render(request, 'sys_mainpage_data_input.html',{'user_name':str(request.user), 'existing_company_scenario_list':existing_company_scenario_list,"file_uploaded_info":file_uploaded_info});





@login_required(redirect_field_name='', login_url='/')
def download_input_data(request, selected_module, selected_com_scen):


    sub_file_name = "data/" + selected_module + "/" + selected_module + "_" + selected_com_scen.split("-")[0] + "_" + selected_com_scen.split("-")[1] + ".xlsx";

    individual_file_name = selected_module + "_" + selected_com_scen.split("-")[0] + "_" + selected_com_scen.split("-")[1] + ".xlsx"

    file_path = os.path.join(settings.MEDIA_ROOT, sub_file_name);
    print (file_path);
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel");
            response['Content-Disposition'] = 'attachment; filename=' + individual_file_name;
            response['X-Sendfile']= smart_str(file_path);
            return response;
    raise Http404;



@login_required(redirect_field_name='', login_url='/')
def download_amr_report(request, file_path):

    sub_file_name = "reports/" + file_path;

    total_file_path = os.path.join(settings.MEDIA_ROOT, sub_file_name);

    individual_file_name = file_path;

    print (total_file_path);
    if os.path.exists(total_file_path):
        with open(total_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel");
            response['Content-Disposition'] = 'attachment; filename=' + individual_file_name;
            response['X-Sendfile']= smart_str(total_file_path);
            return response;
    raise Http404;



def upload_pxq_input_to_kean(pxq_input_list, company, scenario):
    pxq_input.objects.filter(company = company, scenario = scenario).delete();
    #
    # for item in pxq_input_list:
    #     print (item[-1]);

    with connection.cursor() as cursor:
        insert_sql = "INSERT INTO pxq_input (scenario, company, entity, data_source, input_title, period, value) \
                      VALUES (%s,%s,%s,%s,%s,%s,%s);"

        cursor.executemany(insert_sql, pxq_input_list);


def upload_actuals_to_kean(total_actuals_ready_to_kean_list, company, scenario):
    print ("length of total actuals ready to kean list: ", len(total_actuals_ready_to_kean_list));

    actuals.objects.filter(company = company, scenario=scenario).delete();


    for bulk_actual_list in total_actuals_ready_to_kean_list:
        print (len(bulk_actual_list));


        with connection.cursor() as cursor:
            insert_sql = "INSERT INTO actuals (accounting_month, as_of_date, report_date, scenario, company,\
                              entity, plant_id, business_unit_id, account, account_title, bvr_group, project_id, project_name,\
                              period_balance, ending_balance, total_credit, total_debit, reference_number, contract_number,\
                              invoice_id, outage_code, work_order_number, cost_component) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            cursor.executemany(insert_sql, bulk_actual_list);


def upload_budget_to_kean(total_budget_ready_to_kean_list, company, budget_scenario):
    print ("budget_scenario:", budget_scenario);

    print ("length of total actuals ready to kean list: ", len(total_budget_ready_to_kean_list));

    #
    # for item in total_budget_ready_to_kean_list[:5]:
    #     print (item);


    budget.objects.filter(company = company, scenario=budget_scenario).delete();


    for bulk_budget_list in total_budget_ready_to_kean_list:
        print (len(bulk_budget_list));

        # print ([num for num in list(zip(*bulk_budget_list))[6] if '.' not in num ]);

        with connection.cursor() as cursor:
            insert_sql = "INSERT INTO budget (company, scenario, entity, account, account_name, \
                              period, value, model_group, project_id, cost_component_id, work_order_number, \
                              outage_code_id, invoice_id, contract_number_id, reference_number, cost_category, \
                              cost_sub_category, project_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

            cursor.executemany(insert_sql, bulk_budget_list);




def upload_dispatch_to_kean(total_dispatch_ready_to_kean_list, company, scenario):
    print ("length of total dispatch ready to kean list: ", len(total_dispatch_ready_to_kean_list));

    dispatch.objects.filter(company = company, scenario=scenario).delete();


    print (len(total_dispatch_ready_to_kean_list));

    # for item in total_dispatch_ready_to_kean_list:
    #     print (item);


    with connection.cursor() as cursor:
        insert_sql = "INSERT INTO dispatch (scenario, entity, fsli, period, value, company) \
                      VALUES (%s,%s,%s,%s,%s,%s);"

        cursor.executemany(insert_sql, total_dispatch_ready_to_kean_list);


def upload_respreads_to_kean(total_respreads_ready_to_kean_list, company, scenario):
    print ("length of total respreads ready to kean list: ", len(total_respreads_ready_to_kean_list));

    project_respread.objects.filter(company = company, scenario=scenario).delete();

    print (len(total_respreads_ready_to_kean_list));
    with connection.cursor() as cursor:
        insert_sql = "INSERT INTO project_respread (company, scenario, entity, account, account_name,  model_group,\
                      project_id,cost_component_id, work_order_number, outage_code_id,\
                      invoice_id, contract_number_id, reference_number, cost_category, cost_sub_category, project_name, period, value) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

        cursor.executemany(insert_sql, total_respreads_ready_to_kean_list);




def upload_prices_to_kean(total_prices_ready_to_kean_list, company, scenario):
    print ("length of total prices ready to kean list: ", len(total_prices_ready_to_kean_list));

    instrument_id_mapping_list = [];
    with connection.cursor() as cursor:
        raw_query_str = "SELECT * FROM instrument_id_mapping;";
        cursor.execute(raw_query_str);
        for row in cursor.fetchall():
            instrument_id_mapping_list.append([row[1],row[2],row[3]]);


    remapped_ready_to_kean_list = [];



    for i in range(0, len(total_prices_ready_to_kean_list)):

        mapped_instrument_id = [item[2] for item in instrument_id_mapping_list if item[0] == total_prices_ready_to_kean_list[i][-1]][0];

        # print (total_prices_ready_to_kean_list[i][-1],mapped_instrument_id);

        temp_list = list(total_prices_ready_to_kean_list[i][:-1]) + [mapped_instrument_id]
        remapped_ready_to_kean_list.append(temp_list);


    valuation_date = remapped_ready_to_kean_list[0][1];

    prices.objects.filter(scenario=scenario, valuation_date=valuation_date).delete();

    with connection.cursor() as cursor:
        insert_sql = "INSERT INTO prices (scenario, valuation_date, period, price,instrument_id) \
                        VALUES(%s,%s,%s,%s,%s);"

        cursor.executemany(insert_sql, remapped_ready_to_kean_list);
