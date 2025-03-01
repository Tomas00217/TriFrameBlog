from .forms import EmailUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = EmailUserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()

            messages.success(request, "Register successful.")
            return redirect("login")
    else:
        form = EmailUserCreationForm()
    
    return render(request, "registration/register.html", {"form": form})

@login_required(login_url='/accounts/login/')
def profile(request):
    if request.method == "POST":
        new_username = request.POST.get("username")
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Your username has been updated!")
            return redirect("profile")

    return render(request, "accounts/profile.html", {"user": request.user})