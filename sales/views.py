from django.shortcuts import render, redirect, HttpResponse, reverse
from django.conf import settings

from sales.forms import RegisterForm, CustomerForm, ConsultRecordForm
from sales.models import UserInfo, Customer, ConsultRecord
from sales.utils.hashlib_func import set_md5
from sales.utils.page import MyPagination
# Create your views here.


# 添加和编辑跟进记录  和添加编辑客户逻辑和页面一模一样 就是要写一个ModelForm
def add_edit_consult_record(request, rid=None):
    if rid:
        content_title = '编辑跟进信息'
    else:
        content_title = '添加跟进信息'
    consult_obj = ConsultRecord.objects.filter(id=rid).first()
    if request.method == 'GET':
        form_obj = ConsultRecordForm(instance=consult_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=consult_obj)  # 如果是添加客户则instance是None
        if form_obj.is_valid():
            form_obj.save()
            if rid:
                # 如果是编辑客户（cid存在） 则跳转至点击编辑之前的完整url 注意此时的url是form表单默认为空时携带了参数的原url 所以可以直接取值 牛逼！
                return redirect(request.get_full_path().split('next=')[-1])
            else:
                # 如果是添加客户（cid不存在） 则跳转至展示客户页面
                return redirect('consult_record')
    context = {
        'form_obj': form_obj,
        'content_title': content_title,  # base.html中必传的参数
    }
    return render(request, 'add_customer.html', context)


# 跟进记录
def consult_record(request):
    # 只能查看跟进人为当前用户 且状态为未删除的所有跟进记录  ？？？有bug：应该是只能看销售为当前用户的人才对
    consult_record_objs = ConsultRecord.objects.filter(consultant=request.user_obj, delete_status=False).order_by('-id')
    if request.method == 'GET':
        cid = request.GET.get('cid')
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if cid:
            # 查看详情 即该客户的跟进内容
            consult_record_objs = consult_record_objs.filter(customer__id=cid)
        if search_field and kw:
            # 这个是后面添加到context里的 有才添加
            search_dict = {
                'search_field': search_field,
                'kw': kw,
            }
            # 搜索条件 妙啊
            search_field = 'customer__' + search_field + '__contains'
            consult_record_objs = consult_record_objs.filter(**{search_field: kw.strip()})

        per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
        page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
        page_num = request.GET.get('page')  # page_num当前请求的页码数
        total_count = consult_record_objs.count()  # total_count 搜索条件下客户的总个数
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

        html = MyPagination(request, page_num, total_page, page_range_count).get_html()  # 分页组件
        # 倒序排列 [0:10]
        if consult_record_objs:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
            consult_record_objs = consult_record_objs.order_by('-id')[(page_num - 1) * per_page_count:page_num * per_page_count]

    elif request.method == 'POST':
        rids = request.POST.getlist('rids')  # 注意这里是getlist
        option = request.POST.get('options')
        if option == 'delete_record' and rids:
            consult_record_objs.filter(id__in=rids).update(delete_status=True)
            # 返回当前url（携带GET查询条件 相当于只是把POST变成了GET）
        return redirect(request.get_full_path())

    context = {
        'consult_record_objs': consult_record_objs,
        'content_title': '跟进记录',
        'pagination': html,
    }
    # 保留搜索条件
    if request.GET.get('search_field') and request.GET.get('kw'):
        context.update(search_dict)
    return render(request, 'consult_record.html', context=context)


# 添加和编辑客户 合在一起的视图 其实就是编辑客户的一模一样的代码 添加客户也使用 所以就合起来了
def add_edit_customer(request, cid=None):  # 编辑客户时需要带id值 当走的是添加客户的url时cid默认是None
    if cid:
        content_title = '编辑客户'
    else:
        content_title = '添加客户'
    customer_obj = Customer.objects.filter(id=cid).first()  # 如果是添加则customer_obj 是 None
    if request.method == 'GET':
        form_obj = CustomerForm(instance=customer_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=customer_obj)  # 如果是添加客户则instance是None
        if form_obj.is_valid():
            form_obj.save()
            if cid:
                # 如果是编辑客户（cid存在） 则跳转至点击编辑之前的完整url 注意此时的url是form表单默认为空时携带了参数的原url 所以可以直接取值 牛逼！
                return redirect(request.get_full_path().split('next=')[-1])
            else:
                # 如果是添加客户（cid不存在） 则跳转至展示客户页面
                return redirect('customers')
    context = {
        'form_obj': form_obj,
        'content_title': content_title,  # base.html中必传的参数
    }
    return render(request, 'add_customer.html', context)


# 展示客户
def customers(request):
    if request.method == 'POST':
        # 如果是POST请求则是进行公私户转换
        option = request.POST.get('options')
        cids = request.POST.getlist('cids')  # 注意这里要用getlist！！！
        u_obj = request.user_obj
        if option and cids:
            c_obj = Customer.objects.filter(id__in=cids)
            if option == 'reverse_gs':
                # 公转私
                c_obj.update(consultant=u_obj)
            else:
                # 私转公
                c_obj.update(consultant=None)
        return redirect(request.get_full_path())  # 转换后直接返回至原来页面 第几页和查询条件都不变 牛逼啊
    else:
        # 如果是GET请求则展示客户 也可以封装成一个类。
        if request.path == reverse('customers'):
            # 如果是customer这个url过来的请求 就只能查看公户信息
            customers_obj = Customer.objects.filter(consultant=None)
            content_title = '所有公户'  # 这里是content内容的标题
        else:
            content_title = '我的客户'
            # 如果是my_customer这个url过来的请求 就只能查看私户信息
            user_obj = request.user_obj
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

        html = MyPagination(request, page_num, total_page, page_range_count).get_html()  # 分页组件
        # 倒序排列 [0:10]
        if customers_obj:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
            customers_obj = customers_obj.order_by('-id')[(page_num - 1) * per_page_count:page_num * per_page_count]

        context = {
            'customers_obj': customers_obj,
            'pagination': html,
            'content_title': content_title,  # base.html中必传的参数
        }
        # 如果有搜索条件把搜索条件的字典添加到context里
        if search_field and kw:
            context.update(search_dict)
        return render(request, 'customers.html', context=context)


# 登录
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


# 注册
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
