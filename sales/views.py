from django.shortcuts import render, redirect
from sales.forms import RegisterForm

# Create your views here.


def login(request):
    return render(request, 'login.html')


def register(request):
    if request.method == "GET":
        context = {
            'form': RegisterForm,
        }
    elif request.method == 'POST':
        form_obj = RegisterForm(request.POST)
        context = {
            'form': form_obj,
        }
        if form_obj.is_valid():
            return redirect('login')
    return render(request, 'register.html', context=context)
