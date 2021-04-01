from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}!')
            return redirect('login')

        
    else:
        form = RegisterForm()

    return render(response, 'users/register.html', {"form":form})