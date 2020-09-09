import os
import random

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")
    import django
    django.setup()
    from sales import models

    source_type = (('qq', 'qq群'),
                   ('referral', '内部转介绍'),
                   ('website', '官方网站'),
                   ('baidu_ads', '百度推广'),
                   ('office_direct', '直接上门'),
                   ('WoM', '口碑'),
                   ('public class', '公开课'),
                   )
    course_choices = (('LinuxL', 'Linux中高级'),
                      ('PythonFullStack', 'Python全栈高级'),)

    class_type_choices = (('fulltime', '脱产班'),
                          ('online', '网络班'),
                          ('weekend', '周末班'),
                          )
    enroll_status_choices = (
        ('signed', '已报名'),
        ('unsigned', '未报名'),
        ('studying', '学习中'),
        ('paid_in_full', '交全学费'),
    )
    obj_list = []
    for i in range(1, 201):
        d = {
            'qq': str(11111 + i),
            'name': f'技师{i}号',
            'source': random.choice(source_type),
            'course': random.choice(course_choices),
            'class_type': random.choice(class_type_choices),
            'status': random.choice(enroll_status_choices),
        }
        print(d)
        obj = models.Customer(**d)
        obj_list.append(obj)
    models.Customer.objects.bulk_create(obj_list)
