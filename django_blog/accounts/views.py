from .forms import EmailUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages


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