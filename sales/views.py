from django.shortcuts import render, redirect, HttpResponse

from sales.forms import RegisterForm
from sales.models import UserInfo, Customer
from sales.utils.hashlib_func import set_md5
# Create your views here.


def customers(request):
    per_page_count = 10
    page_num = request.GET.get('page')
    total_count = Customer.objects.count()
    shang, yu = divmod(total_count, per_page_count)
    if yu:
        total_page = shang + 1
    else:
        total_page = shang
    page_range_count = 7

    if page_num:
        try:
            page_num = int(page_num)  # 先转成int型 如果输入的不是数字就把它转成1
        except Exception:
            page_num = 1
        if page_num <= 0:  # 如果输入的页码过小重置
            page_num = 1
        elif page_num > total_page:  # 如果输入的页码过大重置
            page_num = total_page
        if page_num <= int(page_range_count/2):
            page_range = range(1, page_range_count+1)
        elif page_num >= (total_page-int(page_range_count/2)):
            page_range = range(total_page-page_range_count, total_page+1)
        else:
            page_range = range(page_num-3, page_num+4)
        customers_obj = Customer.objects.all()[(page_num-1) * per_page_count:page_num * per_page_count]  # [0:10]
    else:
        customers_obj = Customer.objects.all()[:per_page_count]  # [:10]
        page_range = range(1, page_range_count+1)
    context = {
        'customers_obj': customers_obj,
        'page_range': page_range,  # 由于数字不能在模板中for循环 所以得先弄个可迭代对象出来 用range左闭右开
        'last': total_page,  # 这个是用来给最后一页的标签传值用的
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
