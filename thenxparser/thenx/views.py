from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse

@login_required(login_url='thenx:login')
def index(request):
    return HttpResponse("Welcome to the THENX APP.")

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('thenx:index')
    else:
        form = AuthenticationForm()

    return render(request, 'thenx/login.html', {'form':form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('thenx')