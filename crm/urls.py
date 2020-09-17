"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from sales import views

urlpatterns = [
    # 学习记录
    url(r'^study_records/(\d+)', views.study_records, name='study_records'),

    # 编辑课程记录
    url(r'^edit_course_record/(\d+)', views.add_edit_course_record, name='edit_course_record'),
    # 添加课程记录
    url(r'^add_course_record/', views.add_edit_course_record, name='add_course_record'),
    # 课程记录
    url(r'^course_records/', views.course_records, name='course_records'),

    # 编辑报名记录
    url(r'^edit_enrollment/(\d+)', views.add_edit_enrollment, name='edit_enrollment'),
    # 添加报名记录
    url(r'^add_enrollment/', views.add_edit_enrollment, name='add_enrollment'),
    # 查看报名记录 一样的
    url(r'^enrollments/', views.enrollments, name='enrollments'),
    # 编辑跟进记录 和客户一样是同一个视图进行处理
    url(r'^edit_consult_record/(\d+)', views.add_edit_consult_record, name='edit_consult_record'),
    # 添加跟进记录
    url(r'^add_consult_record/', views.add_edit_consult_record, name='add_consult_record'),
    # 跟进记录展示
    url(r'^consult_record/', views.consult_record, name='consult_record'),
    # 我的客户 走的也是customer视图逻辑一样 就是url不同
    url(r'^my_customers/', views.customers, name='my_customers'),
    # 编辑客户 两个url同时匹配同一个视图函数进行处理
    url(r'^edit_customer/(\d+)', views.add_edit_customer, name='edit_customer'),
    #  添加客户
    url(r'^add_customer/', views.add_edit_customer, name='add_customer'),
    #  展示客户
    url(r'^customers/', views.customers, name='customers'),

    url(r'^login/$', views.login, name='login'),
    url(r'^$', views.login, name='login'),

    url(r'^register/$', views.register, name='register'),

    url(r'^admin/', admin.site.urls),
]
