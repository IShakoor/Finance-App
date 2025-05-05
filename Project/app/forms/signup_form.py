from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import CustomUser
from django.core.exceptions import ValidationError
import re

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sfield placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-input'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email Address', 'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-input'})

        # no labels
        for field in self.fields.values():
            field.label = ""

        # pasword requirements
        self.fields['password1'].help_text = """
        - Password must be at least 8 characters
        - Password must include at least one capital letter
        - Password must include at least one number
        - Password must include at least one special character (!@#$%^&*.)
        - Password cannot be the same as your username or email"""

    # fetch users and check if username exists  
    def clean_username(self):
        username = self.cleaned_data.get('username')
        for user in CustomUser.objects.all():
            if user.username.lower() == username.lower():
                raise ValidationError("This username is already taken. Please choose another one.")
        return username

    # fetch users and check if email exists
    def clean_email(self):
        email = self.cleaned_data.get('email')
        for user in CustomUser.objects.all():
            if user.email.lower() == email.lower():
                raise ValidationError("This email is already taken. Please use a different email.")
        return email

    # password checks
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*.]", password):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*.)")

        if username and password.lower() == username.lower():
            raise ValidationError("Password cannot be the same as your username.")

        if email and password.lower() == email.lower():
            raise ValidationError("Password cannot be the same as your email.")

        return password

    # password matches
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password1", "Passwords do not match.")
            return cleaned_data

        return cleaned_data