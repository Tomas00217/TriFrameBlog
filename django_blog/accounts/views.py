from .forms import EmailUserCreationForm, UsernameUpdateForm
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
    form = UsernameUpdateForm(instance=request.user)

    if request.method == "POST":
        form = UsernameUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your username has been updated!")
            return redirect("profile")

    return render(request, "accounts/profile.html", {"form": form})