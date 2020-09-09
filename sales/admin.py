from django.contrib import admin
from sales.models import Campuses, ClassList, Customer, UserInfo
# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('qq', 'name', 'status', 'consultant')


admin.site.register(Campuses)
admin.site.register(ClassList)
admin.site.register(UserInfo)