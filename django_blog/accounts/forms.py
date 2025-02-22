from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import EmailUser


class EmailUserCreationForm(UserCreationForm):

    class Meta:
        model = EmailUser
        fields = ("email",)


class EmailUserChangeForm(UserChangeForm):

    class Meta:
        model = EmailUser
        fields = ("email",)