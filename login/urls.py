from django.conf.urls import include, url;
from . import views;


app_name = 'login'


urlpatterns = [

    url(r'^$', views.load_login_mainpage, name='load_login_mainpage'),
    url(r'^login/', views.check_user_login_info_form, name='check_user_login_info_form'),
    # url(r'^sys_mainpage/',views.load_sys_mainpage ,name='sys_mainpage'),
    url(r'^logout/', views.log_out, name='logout'),

];
