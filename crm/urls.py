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
from sales.views import login, register, customers, add_edit_customer, consult_record, add_edit_consult_record, enrollments, add_edit_enrollment

urlpatterns = [
    # 编辑报名记录
    url(r'^edit_enrollment/(\d+)', add_edit_enrollment, name='edit_enrollment'),
    # 添加报名记录
    url(r'^add_enrollment/', add_edit_enrollment, name='add_enrollment'),
    # 查看报名记录 一样的
    url(r'^enrollments/', enrollments, name='enrollments'),
    # 编辑跟进记录 和客户一样是同一个视图进行处理
    url(r'^edit_consult_record/(\d+)', add_edit_consult_record, name='edit_consult_record'),
    # 添加跟进记录
    url(r'^add_consult_record/', add_edit_consult_record, name='add_consult_record'),
    # 跟进记录展示
    url(r'^consult_record/', consult_record, name='consult_record'),
    # 我的客户 走的也是customer视图逻辑一样 就是url不同
    url(r'^my_customers/', customers, name='my_customers'),
    # 编辑客户 两个url同时匹配同一个视图函数进行处理
    url(r'^edit_customer/(\d+)', add_edit_customer, name='edit_customer'),
    #  添加客户
    url(r'^add_customer/', add_edit_customer, name='add_customer'),
    #  展示客户
    url(r'^customers/', customers, name='customers'),

    url(r'^login/$', login, name='login'),
    url(r'^$', login, name='login'),

    url(r'^register/$', register, name='register'),

    url(r'^admin/', admin.site.urls),
]
