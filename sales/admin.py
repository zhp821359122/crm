from django.contrib import admin
from sales.models import Campuses, ClassList, Customer, UserInfo, ConsultRecord, Enrollment, Department
# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('qq', 'name', 'status', 'consultant')


admin.site.register(Campuses)
admin.site.register(ClassList)
admin.site.register(UserInfo)
admin.site.register(ConsultRecord)
admin.site.register(Enrollment)
admin.site.register(Department)
