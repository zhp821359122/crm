from django.shortcuts import render, redirect, HttpResponse, reverse
from django.conf import settings

from sales.forms import RegisterForm, CustomerForm
from sales.models import UserInfo, Customer
from sales.utils.hashlib_func import set_md5
from sales.utils.page import MyPagination
# Create your views here.


# 添加和编辑客户 合在一起的视图 其实就是编辑客户的一模一样的代码 添加客户也使用 所以就合起来了
def add_edit_customer(request, cid=None):  # 编辑客户时需要带id值 当走的是添加客户的url时cid默认是None
    if cid:
        content_title = '编辑客户'
    else:
        content_title = '添加客户'
    customer_obj = Customer.objects.filter(id=cid).first()  # 如果是添加则customer_obj 是 None
    if request.method == 'GET':
        form_obj = CustomerForm(instance=customer_obj)  # 如果是添加客户 则实例化一个空对象
        context = {
            'form_obj': form_obj,
            'context_title': content_title,
        }
        #  编辑页面这里用的是add_customer.html 共用一套页面
        return render(request, 'add_customer.html', context)
    elif request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=customer_obj)  # 如果是添加客户则instance是None
        if form_obj.is_valid():
            form_obj.save()
            return redirect('customers')
        else:
            context = {
                'form_obj': form_obj,
                'context_title': content_title,
            }
            return render(request, 'add_customer.html', context)


# 展示客户
def customers(request):
    if request.path == reverse('customers'):
        # 如果是customer这个url过来的请求 就只能查看公户信息
        customers_obj = Customer.objects.filter(consultant=None)
    else:
        # 如果是my_customer这个url过来的请求 就只能查看私户信息
        user_obj = UserInfo.objects.get(id=request.session.get('user_id'))
        customers_obj = Customer.objects.filter(consultant=user_obj)
    search_field = request.GET.get('search_field')
    kw = request.GET.get('kw')  # 搜索条件
    if kw and search_field:
        # 原始搜索条件没有加__contains的字典 最后加到context里面 然后渲染到页面中保留搜索框的内容
        search_dict = {
            'search_field': search_field,
            'kw': kw,
        }
        search_field += '__contains'
        kw = kw.strip()
        customers_obj = customers_obj.filter(**{search_field: kw})  # 变量想作为参数只能先做成一个字典
    else:
        customers_obj = customers_obj
    per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
    page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
    page_num = request.GET.get('page')  # page_num当前请求的页码数
    total_count = customers_obj.count()  # total_count 搜索条件下客户的总个数
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

    html = MyPagination(request, page_num, total_page, page_range_count, request.path).get_html()  # 分页组件
    # 倒序排列 [0:10]
    if customers_obj:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
        customers_obj = customers_obj.order_by('-id')[(page_num - 1) * per_page_count:page_num * per_page_count]

    context = {
        'customers_obj': customers_obj,
        'pagination': html,
    }
    # 如果有搜索条件把搜索条件的字典添加到context里
    if search_field and kw:
        context.update(search_dict)
    return render(request, 'customers.html', context=context)


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 用.get会报错
        if UserInfo.objects.filter(username=username, password=set_md5(password)):
            # 登录成功 将用户信息保存到session中
            request.session['user_id'] = UserInfo.objects.get(username=username, password=set_md5(password)).id
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
