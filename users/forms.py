from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms


class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['full_name', ]


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(
        render_value=False, attrs={"class": "form-control", 
        "type": "password", "placeholder": "Enter old password"}))
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput(
        render_value=False, attrs={"class": "form-control", 
        "type": "password", "placeholder": "New password"}))
    new_password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput(
        render_value=False, attrs={"class": "form-control", 
        "type": "password", "placeholder": "Repeat new password"}))

