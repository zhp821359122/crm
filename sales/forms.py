import re
from django import forms
from django.core.exceptions import ValidationError

from sales.models import Customer
from multiselectfield.forms.fields import MultiSelectFormField


# 添加客户页面的ModelForm ModelForm要指定model 直接自动帮你生成 你只需要修改
class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        error_messages = {
            'qq': {'required': 'QQ号码不能为空！！！'},
            'course': {'required': '咨询课程不能为空！！！'},
        }
        widgets = {
            'birthday': forms.widgets.DateInput(attrs={'value': '1999-05-19'}),
            'phone': forms.widgets.TextInput(attrs={'value': '12345678910'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddCustomerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})


# 自定义校验函数 校验手机号码
def moblie_validate(value):
    moblie_re = re.compile(r'^0?(13|14|15|17|18|19)[0-9]{9}$')
    if not moblie_re.match(value):
        raise ValidationError('手机号码格式错误')


# 注册页面的Form From不用指定model 你自己定义字段
class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=3,
        label='用户名',
        widget=forms.widgets.TextInput(attrs={
            'class': 'username',  # 给它添加username属性
            'autocomplete': 'off',
            'placeholder': '输入用户名',
        }),
        error_messages={
            'required': '用户名不能为空',
            'max_length': '用户名不能大于16位',
            'min_length': '用户名不能小于3位',
        }
    )
    password = forms.CharField(
        max_length=32,
        min_length=6,
        label='密码',
        widget=forms.widgets.PasswordInput(attrs={
            'class': 'password',  # 给它添加password属性
            'placeholder': '输入密码',
            'oncontextmenu': 'return false',
            'onpaste': 'return false',
        }),
        error_messages={
            'required': '密码不能为空',
            'max_length': '密码不能大于32位',
            'min_length': '密码不能小于6位',
        }
    )
    # 确认密码
    r_password = forms.CharField(
        max_length=32,
        min_length=6,
        label='确认密码',
        widget=forms.widgets.PasswordInput(attrs={
            'class': 'confirm_password',  # 给它添加confirm_password属性
            'placeholder': '再次输入密码',
            'oncontextmenu': 'return false',
            'onpaste': 'return false',
        }),
        error_messages={
            'required': '确认密码不能为空',
        }
    )

    telephone = forms.CharField(
        label='手机号码',
        validators=[moblie_validate, ],
        widget=forms.widgets.TextInput(attrs={
            'placeholder': '输入手机号码',
            'class': 'phone_number',
        }),
        error_messages={
            'required': '手机号码不能为空',
        }
    )
    email = forms.EmailField(
        label='邮箱',
        # validators=
        widget=forms.widgets.TextInput(attrs={
            'placeholder': '输入邮箱',
            'type': 'email',
            'class': 'email',
        }),
        error_messages={
            'invalid': '邮箱格式不正确',
            'required': '邮箱不能为空',
        }
    )

    def clean(self):
        values = self.cleaned_data
        password = values.get('password')
        r_password = values.get('r_password')

        if password == r_password:
            return values
        else:
            self.add_error('r_password', '两次输入的密码不一致')  # 如果不相等给r_password添加错误信息 如果正确则返回values 不正确则添加错误信息...



