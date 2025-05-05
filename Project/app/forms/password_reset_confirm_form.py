from django import forms
from django.core.exceptions import ValidationError
import re

class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        help_text="""
        - Password must be at least 8 characters
        - Password must include at least one capital letter
        - Password must include at least one number
        - Password must include at least one special character (!@#$%^&*.)
        """
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        help_text="Enter the same password as above, for verification."
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", password1):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not re.search(r"\d", password1):
            raise ValidationError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*.]", password1):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*.)")

        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password1', "Passwords do not match.")

        return cleaned_data