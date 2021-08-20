from django import forms
from django.forms.fields import CharField
from django.forms.forms import Form
from .validators import User

class CreateAccount(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'username',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg'
            }
        ),
        validators=[User.username]
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'email',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg'
            }
        ), 
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'type a strong password',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
                'data-type': 'password'
            }
        ),
        validators=[User.password], label='Password')
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'type password again',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
                'data-type': 'password'
            }
        ),
        validators=[User.password],
        label='Repeat password'
    )

class LoginAccount(forms.Form):
    login = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'your username or email',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg'
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'enter your password',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
                'data-type': 'password'
            }
        ),
        validators=[User.password]
    )

class EditAccount(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'username',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
            }
        ),
        validators=[User.username]
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'email',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg'
            }
        ),
    )
    oldpassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'enter your last password',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
                'data-type': 'password'
            }
        ),
        validators=[User.password],
        label='Old password',
        required=False
    )
    newpassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'enter your new password',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg',
                'data-type': 'password'
            }
        ),
        validators=[User.password],
        label='New password',
        required=False
    )


class ForgotAccount(forms.Form):
    login = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'enter the email or username for your account',
                'class': 'form-control rounded bd-pm-2 bg-bg r-bg'
            }
        ),
        label='Username or Email'
    )