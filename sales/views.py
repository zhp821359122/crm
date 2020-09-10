from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings

from sales.forms import RegisterForm
from sales.models import UserInfo, Customer
from sales.utils.hashlib_func import set_md5
from sales.utils.page import MyPagination
# Create your views here.


def customers(request):
    per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
    page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
    page_num = request.GET.get('page')  # page_num当前请求的页码数
    total_count = Customer.objects.count()  # total_count客户的总个数
    shang, yu = divmod(total_count, per_page_count)
    if yu:
        total_page = shang + 1  # total_page总页码数
    else:
        total_page = shang
    try:
        page_num = int(page_num)  # 先转成int型 如果输入的不是数字就把它转成1
    except Exception:
        page_num = 1
    if page_num <= 0:  # 如果输入的页码过小重置
        page_num = 1
    elif page_num > total_page:  # 如果输入的页码过大重置
        page_num = total_page

    html = MyPagination(page_num, total_page, page_range_count, request.path).get_html()  # 分页组件
    customers_obj = Customer.objects.all()[(page_num - 1) * per_page_count:page_num * per_page_count]  # [0:10]

    context = {
        'customers_obj': customers_obj,
        'pagination': html,
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
