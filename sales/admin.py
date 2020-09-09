from django.contrib import admin
from sales.models import Campuses, ClassList, Customer, UserInfo
# Register your models here.

admin.site.register(Customer)
admin.site.register(Campuses)
admin.site.register(ClassList)
admin.site.register(UserInfo)