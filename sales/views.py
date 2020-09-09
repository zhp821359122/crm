from django.shortcuts import render, redirect, HttpResponse

from sales.forms import RegisterForm
from sales.models import UserInfo, Customer
from sales.utils.hashlib_func import set_md5
# Create your views here.


def customers(request):
    per_page_count = 10
    page_num = request.GET.get('page')
    if page_num:
        customers_obj = Customer.objects.all()[int(page_num) * per_page_count:(int(
            page_num) + 1) * per_page_count]  # [10:20]
    else:
        customers_obj = Customer.objects.all()[:per_page_count]  # [:10]
    context = {
        'customers_obj': customers_obj,
    }
    return render(request, 'customers.html', context=context)


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 用.get会报错
        if UserInfo.objects.filter(username=username, password=set_md5(password)):
            return redirect('customers')
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
