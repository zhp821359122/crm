from django.shortcuts import render, redirect, HttpResponse

from sales.forms import RegisterForm
from sales.models import UserInfo
from sales.utils.hashlib_func import set_md5
# Create your views here.


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 用.get会报错
        if UserInfo.objects.filter(username=username, password=set_md5(password)):
            return render(request, 'base.html')
        else:
            context = {
                'error_msg': '用户名或者密码错误！'
            }
            return render(request, 'login.html', context)


def register(request):
    if request.method == "GET":
        context = {
            'form': RegisterForm,
        }
    elif request.method == 'POST':
        form_obj = RegisterForm(request.POST)
        context = {
            'form': form_obj,
        }
        if form_obj.is_valid():
            form_obj.cleaned_data.pop('r_password')
            form_obj.cleaned_data['password'] = set_md5(form_obj.cleaned_data['password'])
            UserInfo.objects.create(
                **form_obj.cleaned_data,  # 直接**打散可以把字典变成赋值的形式
            )
            return redirect('login')
    return render(request, 'register.html', context=context)
