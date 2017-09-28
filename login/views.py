from django.shortcuts import render, redirect;
from django.http import HttpResponse, HttpResponseRedirect;
from .models import *;
from django.urls import reverse;
from .forms import login_form;
import json;
from django.views.decorators.csrf import csrf_exempt;
from django.contrib.auth import authenticate, login, logout;
from django.contrib.auth.decorators import login_required;
# Create your views here.


def index(request):
    return HttpResponse("Hello KEAN!");

def load_login_mainpage(request):
    if request.user.is_authenticated():
        return redirect('/sys_mainpage/');


    return render(request, 'login.html', {"login_error_msg":"","last_input_email":""});



def check_user_login_info_form(request):
    if request.user.is_authenticated():
        return render(request, 'sys_mainpage.html', {'user_name':str(request.user)});


    if request.method == "POST":
        current_login_form = login_form(request.POST);

        if current_login_form.is_valid():

            input_email = request.POST.get('input_email');
            input_password = request.POST.get('input_password');
            user = authenticate(username=input_email, password=input_password);

            if user and user.is_active:
                login(request, user);
                print ("we succeeded!");
                return HttpResponseRedirect('/sys_mainpage/');
            else:
                last_input_email = request.POST.get('input_email');
                return render(request, 'login.html', {"login_error_msg": "Wrong password.","last_input_email":last_input_email});
    last_input_email = request.POST.get('input_email');
    return render(request, 'login.html', {"login_error_msg": "User email not found.","last_input_email":last_input_email});





@login_required(redirect_field_name='', login_url='/')
def log_out(request):
    logout(request);
    return redirect('/');




#
# def load_sys_mainpage(request):
#     return render(request, 'sys_mainpage.html', {'user_name':'default'});
