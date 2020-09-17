from django.db import models
from multiselectfield import MultiSelectField

from django.utils.safestring import mark_safe
# Create your models here.
course_choices = (('LinuxL',  'Linux中高级'),
                  ('PythonFullStack', 'Python全栈高级'),)

class_type_choices = (('fulltime', '脱产班'),
                      ('online', '网络班'),
                      ('weekend', '周末班'),
                      )
source_type = (('qq', 'qq群'),
               ('referral', '内部转介绍'),
               ('website', '官方网站'),
               ('baidu_ads', '百度推广'),
               ('office_direct', '直接上门'),
               ('WoM', '口碑'),
               ('public class', '公开课'),
               )
enroll_status_choices = (
    ('signed', '已报名'),
    ('unsigned', '未报名'),
    ('studying', '学习中'),
    ('paid_in_full', '交全学费'),
)

score_choices = (
    (100, 'A+'),
    (90, 'A'),
    (85, 'B+'),
    (80, 'B'),
    (70, 'B-'),
    (60, 'C+'),
    (50, 'C'),
    (40, 'C-'),
    (0, 'D'),
    (-1, 'N/A'),
    (-100, 'COPY'),
    (-1000, 'FAIL'),
)

seek_status_choices = (
    ('A', '近期无报名计划'),
    ('B', '1个月内报名'),
    ('C', '2周内报名'),
    ('D', '1周内报名'),
    ('E', '定金'),
    ('F', '到班'),
    ('G', '全款'),
    ('H', '无效'),
)
# pay_type_choices = (
#     ('deposite', '订金/报名费'),
#     ('tuition', '学费'),
#     ('transfer', '转班'),
#     ('dropout', '退学'),
#     ('refund', '退款'),
# )
attendance_choices = (
    ('checked', '已签到'),
    ('vacate', '请假'),
    ('late', '迟到'),
    ('absence', '缺勤'),
    ('leave_early', '早退'),
)


class CourseRecord(models.Model):
    """
    课程记录表
    """
    day_num = models.IntegerField('节次', help_text='此处填写第几节课或者第几天课程...必须为数字')
    date = models.DateField(auto_now_add=True, verbose_name='上课时间')
    course_title = models.CharField('本节课程标题', max_length=64, blank=True, null=True)
    course_memo = models.TextField('本节课程内容', max_length=300, blank=True, null=True)
    has_homework = models.BooleanField(default=True, verbose_name='本节课有作业')
    homework_title = models.CharField('本节作业标题', max_length=64, blank=True, null=True)
    homework_memo = models.TextField('作业描述', max_length=500, blank=True, null=True)
    scoring_point = models.TextField('得分点', max_length=300, blank=True, null=True)
    re_class = models.ForeignKey('ClassList', verbose_name='班级')
    teacher = models.ForeignKey('UserInfo', verbose_name='讲师')

    class Meta:
        unique_together = ('re_class', 'day_num')
        verbose_name = '课程记录表'
        verbose_name_plural = '课程记录表'

    def __str__(self):
        return self.re_class.course + '第' + str(self.re_class.semester) + '期:第' + str(self.day_num) + '节课'


class StudyRecord(models.Model):
    """
    学习记录表
    """
    attendance = models.CharField('考勤', choices=attendance_choices, default='checked', max_length=64)
    score = models.IntegerField('本节成绩', choices=score_choices, default=1)
    homework_note = models.CharField(max_length=255, verbose_name='作业批语', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField('备注', max_length=255, blank=True, null=True)
    homework = models.FileField(verbose_name='作业文件', blank=True, null=True)
    course_record = models.ForeignKey('CourseRecord', verbose_name='某节课程')
    student = models.ForeignKey('Customer', verbose_name='学员')

    class Meta:
        unique_together = ('course_record', 'student')
        verbose_name = '学习记录表'
        verbose_name_plural = '学习记录表'

    def __str__(self):
        return self.student.name + ':' + self.course_record.re_class.campuses.name + self.course_record.re_class.course + ':' + str(self.course_record.re_class.semester) + ':' + str(self.course_record.day_num)


class Enrollment(models.Model):
    """
    报名表
    """
    why_us = models.TextField('为什么报名', max_length=1024, default=None, blank=True, null=True)
    your_expectation = models.TextField('学完想达到的具体期望', max_length=1024, blank=True, null=True)
    contract_approved = models.BooleanField('审批通过', help_text='在审阅完学员的资料无误后勾选此项，合同即生效', default=False)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name='报名日期')
    memo = models.CharField('备注', max_length=64, blank=True, null=True)
    delete_status = models.BooleanField('删除状态', default=False)
    customer = models.ForeignKey('Customer', verbose_name='客户名称')
    school = models.ForeignKey('Campuses')
    enrolment_class = models.ForeignKey('ClassList', verbose_name='所报班级')

    class Meta:
        unique_together = ('enrolment_class', 'customer')
        verbose_name = '报名表'
        verbose_name_plural = '报名表'

    def __str__(self):
        return self.customer.name + ':' + self.enrolment_class.get_course_display()


class ConsultRecord(models.Model):
    """
    跟进记录表
    """
    customer = models.ForeignKey('Customer', verbose_name='所咨询客户')
    note = models.TextField(verbose_name='跟进内容')
    status = models.CharField('跟进状态', max_length=8, choices=seek_status_choices, help_text='选择客户此时的状态')
    consultant = models.ForeignKey('UserInfo', verbose_name='跟进人', related_name='records')
    # 展示跟进记录的时候应该是按客户来划分的呀...就是说当前的客户是我的 然后我点击跟进记录 应该是能看到属于我的用户的所有跟进记录 就算是之前别的用户（如果他辞职了）跟进过的应该也能看见才对...
    # 所以展示跟进记录时本应该先根据当前用户的id查找出所有私户的id 然后根据私户的id查找出所有该客户的跟进记录
    # 但是我们规定好了当前用户只能查看自己的跟进记录 如果是其他用户对该客户的跟进记录 需要让他手动调给你看
    date = models.DateTimeField('跟进日期', auto_now_add=True)
    delete_status = models.BooleanField('删除状态', default=False)

    def __str__(self):
        return str(self.customer) + '  销售' + str(self.consultant)

    class Meta:
        verbose_name = '跟进记录表'
        verbose_name_plural = '跟进记录表'


class Department(models.Model):
    """
    部门表
    """
    name = models.CharField(max_length=12, verbose_name='部门名称')
    count = models.IntegerField(verbose_name='部门人数')  # 这个部门人数是假的 还没有根据用户统计

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门表'
        verbose_name_plural = '部门表'


class UserInfo(models.Model):
    """
    用户表：销售...
    """
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    telephone = models.CharField(max_length=16)
    is_active = models.BooleanField(default=True)
    depart = models.ForeignKey('Department', default=1)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = '用户表'


class Customer(models.Model):
    """
    客户表：最开始的时候大家都是客户
    """
    qq = models.CharField(verbose_name='QQ', max_length=32, unique=True, help_text='QQ号必须唯一')
    qq_name = models.CharField('QQ昵称', max_length=32, blank=True, null=True)  # blank 和 null配合用 blank是校验时可以为空 null是存进数据库
    name = models.CharField('姓名', max_length=32, blank=True, null=True, help_text='学员报名后，请修改为真实姓名')
    sex_type = (('male', '男'), ('female', '女'))
    sex = models.CharField('性别', choices=sex_type, default='male', blank=True, null=True, max_length=16)
    birthday = models.DateField('出生日期', default=None, help_text='格式：yyyy-mm-dd', blank=True, null=True)
    phone = models.CharField('手机号', blank=True, null=True, max_length=12)
    source = models.CharField('客户来源', max_length=32, choices=source_type, default='qq')
    # self是本表 也可以直接写Customer 关联本表id字段（一对多关系）
    introduce_from = models.ForeignKey('self', verbose_name='转介绍自学员', blank=True, null=True, on_delete=models.CASCADE)

    # 多选Field原生的Form没有 需要手动安装 django-multiselectfield
    course = MultiSelectField('咨询课程', choices=course_choices)
    class_type = models.CharField('班级类型', max_length=64, choices=class_type_choices, default='fulltime')
    customer_note = models.TextField('客户备注', blank=True, null=True)
    status = models.CharField(
        '状态',
        choices=enroll_status_choices,
        max_length=64, default='unsigned',
        help_text='选择客户此时的状态',  # help_text 是针对admin应用里的
    )
    date = models.DateTimeField('咨询日期', auto_now_add=True)
    last_consult_date = models.DateField('最后跟进日期', auto_now_add=True)
    next_date = models.DateField('预计下次跟进日期', blank=True, null=True)
    consultant = models.ForeignKey('UserInfo', verbose_name='销售',
                                   related_name='customers', blank=True,  # 这个related_name是什么
                                   null=True, on_delete=models.CASCADE)
    class_list = models.ManyToManyField('ClassList', verbose_name='已报班级', blank=True)

    def __str__(self):
        return str(self.name) + ':'+self.qq

    class Meta:
        verbose_name = '客户表'
        verbose_name_plural = '客户表'

    @property
    def get_status_show(self):
        color_dict = {
              'signed': 'lightblue',
              'unsigned': 'red',
              'studying': 'lightgreen',
              'paid_in_full': 'lightgreen',
        }
        html = '<span style="background-color:{}">{}</span>'.format(color_dict[self.status],  self.get_status_display())
        return mark_safe(html)


class Campuses(models.Model):
    """
    校区表
    """
    name = models.CharField(verbose_name='校区', max_length=32)
    address = models.CharField(verbose_name='详细地址', max_length=124, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '校区表'
        verbose_name_plural = '校区表'


class ClassList(models.Model):
    """
    班级表
    """
    course = models.CharField('课程名称', max_length=64, choices=course_choices)
    semester = models.IntegerField('学期')
    campuses = models.ForeignKey('Campuses', verbose_name='校区', on_delete=models.CASCADE)
    price = models.IntegerField('学费', default=10000)
    memo = models.CharField('说明', blank=True, null=True, max_length=100)
    start_date = models.DateField('开班日期')
    graduate_date = models.DateField('结业日期', blank=True, null=True)
    teachers = models.ManyToManyField('UserInfo', verbose_name='老师')
    class_type = models.CharField(choices=class_type_choices, max_length=64, verbose_name='班额及类型', blank=True, null=True)

    class Meta:
        unique_together = ('course', 'semester', 'campuses')  # 定义联合唯一...
        verbose_name = '班级表'
        verbose_name_plural = '班级表'

    def __str__(self):
        return self.course + '-' + str(self.semester) + '-' + self.campuses.name

