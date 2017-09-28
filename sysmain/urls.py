from django.conf.urls import include, url;
from . import views;


app_name = 'sysmain'


urlpatterns = [

    url(r'^$', views.load_sys_mainpage, name='sys_mainpage_home'),
    url(r'^pjm_lmp$', views.load_sys_mainpage_pjmlmp, name='sys_mainpage_pjmlmp'),
    url(r'^sys_amr_dashboard$', views.load_sys_amr_dashboard, name='sys_amr_dashboard'),
    url(r'^pjm_api_call$', views.pjm_api_call, name='pjm_api_call'),
    url(r'^amr$', views.load_amr, name='load_amr'),
    url(r'^run_amr$', views.run_amr, name='run_amr'),
    url(r'^checkview$', views.checkview, name='checkview'),
    url(r'^calc_control$', views.calc_control, name='calc_control'),
    url(r'^check_financials_status/(?P<selected_com_scen>[A-Za-z0-9\s\-]+)/$', views.check_financials_status, name='check_financials_status'),
    url(r'^check_version_status/(?P<selected_com_scen>[A-Za-z0-9\s\-]+)/(?P<selected_version>[A-Za-z0-9\s\-]+)/$', views.check_version_status, name='check_version_status'),
    url(r'^upload_pjmlmp_to_kean/$', views.upload_pjmlmp_to_kean, name='upload_pjmlmp_to_kean'),
    url(r'^initiate_amr/(?P<new_com_scen>[A-Za-z0-9\s\-]+)/$', views.initiate_amr, name='initiate_amr'),
    url(r'^data_prepare$', views.data_prepare, name='data_prepare'),
    url(r'^upload_input_data$', views.upload_input_data, name='upload_input_data'),
    url(r'^download_input_data/module=(?P<selected_module>[A-Za-z]+)&com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)$', views.download_input_data, name='download_input_data'),
    url(r'^run_budget/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&budget_scenario=(?P<budget_scenario>[A-Za-z0-9\s\-]+)$', views.run_budget, name='run_budget'),
    url(r'^run_budget_for_forecast_period/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&budget_scenario=(?P<budget_scenario>[A-Za-z0-9\s\-]+)$', views.run_budget_for_forecast_period, name='run_budget_for_forecast_period'),
    url(r'^amr_report$', views.run_amr_report, name='run_amr_report'),
    url(r'^initiate_amr_report/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)$', views.initiate_amr_report, name='initiate_amr_report'),
    url(r'^generate_amr_report/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&amr_version=(?P<amr_version>[A-Za-z0-9\s]+)&budget_scenario=(?P<budget_scenario>[A-Za-z0-9\s\-]+)$', views.generate_amr_report, name='generate_amr_report'),
    url(r'^download_amr_report/file_path=(?P<file_path>[A-Za-z0-9\s\-\.\/\_]+)$', views.download_amr_report, name='download_amr_report'),
    url(r'^generate_fy_report/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&version_year=(?P<version_year>[A-Za-z0-9\s\-]+)$', views.generate_fy_report, name='generate_fy_report'),
    url(r'^generate_variance_report/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&amr_version=(?P<amr_version>[A-Za-z0-9\s]+)&budget_scenario=(?P<budget_scenario>[A-Za-z0-9\s\-]+)$', views.generate_variance_report, name='generate_variance_report'),
    url(r'^check_company_status/selected_company=(?P<selected_company>[A-Za-z0-9]+)$', views.check_company_status, name='check_company_status'),
    url(r'^generate_diff_report/first_svy=(?P<first_svy>[A-Za-z0-9\s\-]+)&second_svy=(?P<second_svy>[A-Za-z0-9\s\-]+)&selected_company=(?P<selected_company>[A-Za-z0-9\s\-]+)$', views.generate_diff_report, name='generate_diff_report'),
    url(r'^run_liquidity/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&amr_version=(?P<amr_version>[A-Za-z0-9\s]+)$', views.run_liquidity, name='run_liquidity'),
    url(r'^make_version/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&input_version=(?P<input_version>[A-Za-z0-9\s]+)$', views.make_version, name='make_version'),
    url(r'^run_pxq/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&amr_version=(?P<amr_version>[A-Za-z0-9\s]+)&budget_scenario=(?P<budget_scenario>[A-Za-z0-9\s]+)$', views.run_pxq, name='run_pxq'),
    url(r'^copy_from_selected/current_com_scen=(?P<current_com_scen>[A-Za-z0-9\s\-]+)&selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&fsli=(?P<fsli>[A-Za-z0-9\s]+)&module=(?P<module>[A-Za-z0-9\s\_]+)$', views.copy_from_selected, name='copy_from_selected'),
    url(r'^plot_bvr/selected_com_scen=(?P<selected_com_scen>[A-Za-z0-9\s\-]+)&selected_entity=(?P<selected_entity>[A-Za-z0-9]+)&selected_fsli=(?P<selected_fsli>[A-Za-z0-9\s]+)$', views.plot_bvr, name='plot_bvr'),


];
