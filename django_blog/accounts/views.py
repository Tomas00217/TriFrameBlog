from .forms import EmailUserCreationForm, EmailUserLoginForm, UsernameUpdateForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

def email_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("index")

    if request.method == "POST":
        form = EmailUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                messages.success(request, "Login successful.")
                return redirect("index")
            else:
                form.add_error(None, "Your email and password did not match. Please try again.")

        return render(request, "registration/login.html", {"form": form}, status=400)
    else:
        form = EmailUserLoginForm()

    return render(request, "registration/login.html", {"form": form})

def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already registered.")
        return redirect("index")

    if request.method == "POST":
        form = EmailUserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()

            messages.success(request, "Register successful.")
            return redirect("login")

        return render(request, "registration/register.html", {"form": form}, status=400)
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

        return render(request, "accounts/profile.html", {"form": form}, status=400)

    return render(request, "accounts/profile.html", {"form": form})