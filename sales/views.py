from django.shortcuts import render, redirect, HttpResponse, reverse
from django.conf import settings
from django.forms.models import modelformset_factory

from sales import forms
from sales import models
from sales.utils.hashlib_func import set_md5
from sales.utils.page import MyPagination
# Create your views here.


# 增加学习记录  别忘了还有默认值参数！！！在ModelFormSet的时候不传不就好了
def add_study_record(request, cid):
    # 适用场景：新增一名新的学员  手动添加学习记录
    content_title = '添加学习记录'
    if request.method == 'GET':
        form_obj = forms.StudyRecordForm(cid)
    elif request.method == 'POST':
        form_obj = forms.StudyRecordForm(cid, request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('course_records')
    context = {
        'form_obj': form_obj,
        'content_title': content_title,  # base.html中必传的参数
    }
    return render(request, 'add_study_record.html', context)


# 查看学习记录  添加学习记录由于formset不能接受modelform初始化的参数...所以暂时不能单独做 很棘手先不处理
def study_records(request, course_record_id):
    # 使用modelformset批量编辑保存  分页的话一样的form_set[:1] 主要是要统计出数量
    # 想要排序的话不能直接操作ModelFormSet但是可以先把queryset排序了 如下：
    study_record_objs = models.StudyRecord.objects.filter(course_record__id=course_record_id).order_by('-id')
    form_set = modelformset_factory(model=models.StudyRecord, form=forms.StudyRecordForm, extra=0)
    if request.method == 'GET':
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if search_field and kw:
            # 这个是后面添加到context里的 有才添加
            kw = kw.strip()
            search_dict = {
                'search_field': search_field,
                'kw': kw,
            }
            search_field = 'student__name__contains'
            study_record_objs = study_record_objs.filter(**{search_field: kw})

    elif request.method == 'POST':
        option = request.POST.get('options')
        print(option)
        students_id = request.POST.getlist('students_id')
        if option == 'delete_record' and students_id:
            # 删除学习记录 我只要拿到student_id还有课程id就行了 不一定要拿学习记录id 通过student_id和课程id找到对应的学习记录
            models.StudyRecord.objects.filter(student__id__in=students_id, course_record__id=course_record_id).delete()
        else:
            # 如果option和students_id存在则删除学习记录 否则执行保存formset的操作
            form_set = form_set(request.POST)
            if form_set.is_valid():
                form_set.save()
        return redirect('course_records')
    # 由于分页是把formset变成了list类型 会丢失management_form等属性
    # 分页可以先将models筛选然后再给form_set赋值 因为form_set中有多少model那么form.id就得是多少 这样就实现了分页 太6了 搜索也是同理。
    per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
    page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
    page_num = request.GET.get('page')  # page_num当前请求的页码数
    total_count = study_record_objs.count()  # total_count 搜索条件下客户的总个数
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
    # if study_record_objs:  这样判断会报错 ！！！
    if study_record_objs.count() != 0:
        study_record_objs = study_record_objs[
                            (page_num - 1) * per_page_count:page_num * per_page_count]
    # try:
    #     study_record_objs = study_record_objs[
    #                         (page_num - 1) * per_page_count:page_num * per_page_count]
    # except Exception:
    #     pass

    # 最后在设置form_set
    form_set = form_set(queryset=study_record_objs)  # 这里为啥不能用.id？？？
    # 这里传一个flag用来判断是否有展示数据 如果有才显示分页和按钮 优化一下
    if study_record_objs:
        flag = True
    else:
        flag = False
    context = {
        'flag': flag,
        'form_set': form_set,
        'content_title': '学习记录',
        'pagination': html,
        'course_record_id': course_record_id,
    }
    if request.GET.get('search_field') and request.GET.get('kw'):
        context.update(search_dict)
    print(form_set)
    return render(request, 'study_records.html', context=context)


# 添加和编辑课程记录
def add_edit_course_record(request, cid=None):
    # bug : 如果将某条记录删除了 再次添加联合字段相同的记录时 会添加不了
    if cid:
        content_title = '编辑课程信息'
    else:
        content_title = '添加课程信息'
    course_record_obj = models.CourseRecord.objects.filter(id=cid).first()
    if request.method == 'GET':
        form_obj = forms.CourseRecordForm(instance=course_record_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = forms.CourseRecordForm(request.POST, instance=course_record_obj)  # 如果是添加客户则instance是None
        if form_obj.is_valid():
            form_obj.save()
            if cid:
                # 如果是编辑客户（cid存在） 则跳转至点击编辑之前的完整url 注意此时的url是form表单默认为空时携带了参数的原url 所以可以直接取值 牛逼！
                return redirect(request.get_full_path().split('next=')[-1])
            else:
                # 如果是添加客户（cid不存在） 则跳转至展示客户页面
                return redirect('course_records')
    context = {
        'form_obj': form_obj,
        'content_title': content_title,  # base.html中必传的参数
    }
    return render(request, 'add_consult_record.html', context)


# 课程记录
def course_records(request):
    course_record_objs = models.CourseRecord.objects.all()
    if request.method == 'GET':
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if search_field and kw:
            # 这个是后面添加到context里的 有才添加
            search_dict = {
                'search_field': search_field,
                'kw': kw,
            }
            # 搜索条件
            if search_field == 'day_num':
                try:
                    kw = int(kw.strip())
                except Exception:
                    kw = None
                course_record_objs = course_record_objs.filter(**{search_field: kw})

        per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
        page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
        page_num = request.GET.get('page')  # page_num当前请求的页码数
        total_count = course_record_objs.count()  # total_count 搜索条件下客户的总个数
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
        # 把最后的结果根据时间倒序排列 [0:10]每次取出10个 这里如果数值超出了索引不会报错...
        if course_record_objs:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
            course_record_objs = course_record_objs.order_by('-id')[
                              (page_num - 1) * per_page_count:page_num * per_page_count]

    elif request.method == 'POST':
        cids = request.POST.getlist('cids')  # 注意这里是getlist
        option = request.POST.get('options')
        if option == 'bulk_create_study_records' and cids:
            # 批量生成学习记录 只需要传两个参数 一个是课程 一个是学员
            for cid in cids:
                cid = int(cid)
                course_record_obj_to_bulk = models.CourseRecord.objects.filter(id=cid).first()
                # student_objs = models.Customer.objects.filter(class_list__id=course_record_obj_to_bulk.re_class.id)
                # 注意这里必须带一个filter 不然会报错 判断某个字段不为空__isnull=False
                student_objs = course_record_obj_to_bulk.re_class.customer_set.filter(status='studying')
                bulk_list = []
                for student_obj in student_objs:
                    bulk_list.append(models.StudyRecord(
                        student=student_obj,
                        course_record=course_record_obj_to_bulk,
                    ))
                try:
                    # 如果重复选择了课程就返回一个页面告知一下
                    models.StudyRecord.objects.bulk_create(bulk_list)
                except Exception:
                    return HttpResponse('所选课程中存在已创建学习记录的课程，请勿重复创建学习记录！！！')
            # 返回当前url（携带GET查询条件 相当于只是把POST变成了GET）
        return redirect(request.get_full_path())

    context = {
        'course_record_objs': course_record_objs,
        'content_title': '课程记录',
        'pagination': html,
    }
    # 保留搜索条件
    if request.GET.get('search_field') and request.GET.get('kw'):
        context.update(search_dict)
    return render(request, 'course_records.html', context=context)


# 添加和编辑报名记录
def add_edit_enrollment(request, eid=None):
    # bug : 如果将某条记录删除了 再次添加联合字段相同的记录时 会添加不了
    if eid:
        content_title = '编辑报名信息'
    else:
        content_title = '添加报名信息'
    enrollment_obj = models.Enrollment.objects.filter(id=eid).first()
    if request.method == 'GET':
        form_obj = forms.EnrollmentForm(request, instance=enrollment_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = forms.EnrollmentForm(request, request.POST, instance=enrollment_obj)  # 如果是添加客户则instance是None
        if form_obj.is_valid():
            form_obj.save()
            if eid:
                # 如果是编辑客户（cid存在） 则跳转至点击编辑之前的完整url 注意此时的url是form表单默认为空时携带了参数的原url 所以可以直接取值 牛逼！
                return redirect(request.get_full_path().split('next=')[-1])
            else:
                # 如果是添加客户（cid不存在） 则跳转至展示客户页面
                return redirect('enrollments')
    context = {
        'form_obj': form_obj,
        'content_title': content_title,  # base.html中必传的参数
    }
    return render(request, 'add_enrollment.html', context)


# 查看报名记录 复制粘贴照葫芦画瓢
def enrollments(request):
    # 只能查看当前用户的私户的所有状态为未删除的报名信息
    enrollment_objs = models.Enrollment.objects.filter(customer__consultant=request.user_obj, delete_status=False)
    if request.method == 'GET':
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if search_field and kw:
            # 这个是后面添加到context里的 有才添加
            search_dict = {
                'search_field': search_field,
                'kw': kw,
            }
            # 搜索条件
            if search_field == 'course':
                search_field = 'enrolment_class__course__contains'
            elif search_field == 'name':
                search_field = 'customer__name__contains'
                enrollment_objs = enrollment_objs.filter(**{search_field: kw.strip()})

        per_page_count = settings.PER_PAGE_COUNT  # per_page_count每页加载的客户数量
        page_range_count = settings.PAGE_RANGE_COUNT  # page_range_count分页组件加载的页码数
        page_num = request.GET.get('page')  # page_num当前请求的页码数
        total_count = enrollment_objs.count()  # total_count 搜索条件下客户的总个数
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
        # 把最后的结果根据时间倒序排列 [0:10]每次取出10个 这里如果数值超出了索引不会报错...
        if enrollment_objs:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
            enrollment_objs = enrollment_objs.order_by('-enrolled_date')[(page_num - 1) * per_page_count:page_num * per_page_count]

    elif request.method == 'POST':
        eids = request.POST.getlist('eids')  # 注意这里是getlist
        option = request.POST.get('options')
        if option == 'delete_enrollment' and eids:
            enrollment_objs.filter(id__in=eids).update(delete_status=True)
            # 返回当前url（携带GET查询条件 相当于只是把POST变成了GET）
        return redirect(request.get_full_path())

    context = {
        'enrollment_objs': enrollment_objs,
        'content_title': '报名记录',
        'pagination': html,
    }
    # 保留搜索条件
    if request.GET.get('search_field') and request.GET.get('kw'):
        context.update(search_dict)
    return render(request, 'enrollments.html', context=context)


# 添加和编辑跟进记录  和添加编辑客户逻辑和页面一模一样 就是要写一个ModelForm
def add_edit_consult_record(request, rid=None):
    if rid:
        content_title = '编辑跟进信息'
    else:
        content_title = '添加跟进信息'
    consult_obj = models.ConsultRecord.objects.filter(id=rid).first()
    if request.method == 'GET':
        form_obj = forms.ConsultRecordForm(request, instance=consult_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = forms.ConsultRecordForm(request, request.POST, instance=consult_obj)  # 如果是添加客户则instance是None
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


# 跟进记录  直接展示跟进内容 如果很长的话页面样式会很乱。
def consult_record(request):
    # 只能查看当前用户的私户的所有状态为未删除的跟进记录
    consult_record_objs = models.ConsultRecord.objects.filter(customer__consultant=request.user_obj, delete_status=False)
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
        # 把最后的结果根据时间倒序排列 [0:10]每次取出10个 这里如果数值超出了索引不会报错...
        if consult_record_objs:  # 如果没有搜索条件匹配的结果就不用取索引了 否则会报错
            consult_record_objs = consult_record_objs.order_by('-date')[(page_num - 1) * per_page_count:page_num * per_page_count]

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
    customer_obj = models.Customer.objects.filter(id=cid).first()  # 如果是添加则customer_obj 是 None
    if request.method == 'GET':
        form_obj = forms.CustomerForm(instance=customer_obj)  # 如果是添加客户 则实例化一个空对象
    elif request.method == 'POST':
        form_obj = forms.CustomerForm(request.POST, instance=customer_obj)  # 如果是添加客户则instance是None
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
            c_objs = models.Customer.objects.filter(id__in=cids)
            if option == 'reverse_gs':
                # 公转私要考虑多用户同时操作 判断queryset中每一个object的consultant的值是否为None queryset才有update方法
                # 当客户的consultant不为空时如何增加一个提示让用户知道该客户已经被选择了？？？可以返回一个提示页面 或者你用Ajax
                if c_objs.filter(consultant=None).count() == len(cids):
                    c_objs.update(consultant=request.user_obj)
                elif not c_objs.filter(consultant=None):
                    return HttpResponse('您选择的所有客户已经被他人选择！！！')
                else:
                    c_objs.filter(consultant=None).update(consultant=request.user_obj)
                    return HttpResponse('您选择的客户中有些客户已经被他人选择')
            else:
                # 私转公
                c_objs.update(consultant=None)
        return redirect(request.get_full_path())  # 转换后直接返回至原来页面 第几页和查询条件都不变 牛逼啊
    else:
        # 如果是GET请求则展示客户 也可以封装成一个类。
        if request.path == reverse('customers'):
            # 如果是customer这个url过来的请求 就只能查看公户信息
            customers_obj = models.Customer.objects.filter(consultant=None)
            content_title = '所有公户'  # 这里是content内容的标题
        else:
            content_title = '我的客户'
            # 如果是my_customer这个url过来的请求 就只能查看私户信息
            user_obj = request.user_obj
            customers_obj = models.Customer.objects.filter(consultant=user_obj)
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
        if models.UserInfo.objects.filter(username=username, password=set_md5(password)):
            # 登录成功 将用户信息保存到session中
            request.session['user_id'] = models.UserInfo.objects.get(username=username, password=set_md5(password)).id
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
            'form': forms.RegisterForm,
        }
    elif request.method == 'POST':
        form_obj = forms.RegisterForm(request.POST)
        context = {
            'form': form_obj,
        }
        if form_obj.is_valid():
            form_obj.cleaned_data.pop('r_password')
            form_obj.cleaned_data['password'] = set_md5(form_obj.cleaned_data['password'])
            models.UserInfo.objects.create(
                **form_obj.cleaned_data,  # 直接**打散可以把字典变成赋值的形式
            )
            return redirect('login')
    return render(request, 'register.html', context=context)
