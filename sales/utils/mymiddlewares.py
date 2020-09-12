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
        user_id = request.session.get('user_id')
        if user_id:  # 如果有的话就返回None
            request.user = UserInfo.objects.get(id=user_id)  # 直接把用户对象封装到request里面 这样视图中就能直接用
            return
        else:
            return redirect('login')  # 如果没有则返回跳转至login页面
