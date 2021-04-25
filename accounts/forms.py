from django import forms
from django.contrib import auth
from django.contrib.auth import (
    authenticate,
    get_user_model
)
from django.contrib.auth.models import User
from django.forms.widgets import EmailInput, PasswordInput

User = get_user_model()

class UserLoginForm(forms.Form):
    password = forms.CharField(widget=PasswordInput(attrs={'class':'class="input100"', 'placeholder' : 'Password'}))
    username = forms.CharField(label = 'Username', help_text="", widget= forms.TextInput
                           (attrs={'class':'class="input100"', 'placeholder' : 'UName'}))

    field_order = ['username', 'password']
    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username = username, password = password)
            if not user:
                raise forms.ValidationError("User does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Passwo   rd")
            if not user.is_active:
                raise forms.ValidationError("This user is not active")
        
        return super(UserLoginForm, self).clean(*args, **kwargs)
    
class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email Address', widget=EmailInput(
        attrs={'id' : 'your-email', 'class' : 'input-text', 'placeholder' : "Email Address" }
    ))
    email2 = forms.EmailField(label='Confirm Email', widget=EmailInput(
        attrs={'id' : 'your-email', 'class' : 'input-text', 'placeholder' : "Confirm Email Address" }
    ))
    password = forms.CharField(widget=PasswordInput(attrs={'id' : "password", 'class' : 'input-text' , 'placeholder' : "Password"}))
    password1 = forms.CharField(widget=PasswordInput(attrs={'id' : "password1", 'class' : 'input-text' , 'placeholder' : "Confirm Password"}))
    username = forms.CharField(label = 'Username', help_text="", widget= forms.TextInput
                           (attrs={'id' : "full-name", 'class' : "input-text" , 'placeholder' : "Username"}))
    class Meta:
        model = User
        feilds = [
            'email',
            'email2',
            'username',
            'password'
        ]
        exclude = [
            'first_name',
            'last_name',
            'groups',
            'user_permissions',
            'is_staff',
            'is_active',
            'is_superuser',
            'last_login',
            'date_joined'
        ]
    field_order = ['username', 'email','email2', 'password']
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email != email2:
            raise forms.ValidationError("Emails must match")
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError(
                "This email has already been registered")
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        if password != password1:
            raise forms.ValidationError('Passwords must match')
        if len(password) > 15:
            raise forms.ValidationError('Password must be less than 15 chars')
        return super(UserRegisterForm, self).clean(*args, **kwargs)