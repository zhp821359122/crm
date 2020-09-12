from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,reverse

from sales.models import UserInfo


class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        white_list = [
            reverse('login'),
            reverse('register'),
        ]
        if request.path in white_list:
            return
        user_obj = UserInfo.objects.filter(id=request.session.get('user_id')).first()
        if user_obj:  # 如果有的话就返回None
            return
        else:
            return redirect('login')  # 如果没有则返回跳转至login页面
