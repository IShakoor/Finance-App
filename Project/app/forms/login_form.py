from django import forms
from app.models import CustomUser

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'})
    )

    # check login details with database
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # find user details
        if email and password:
            found_user = None
            for user in CustomUser.objects.all():
                if user.email.lower() == email.lower():
                    found_user = user
                    break
            
            if not found_user:
                raise forms.ValidationError("Invalid email or password.")
            
            # check password
            if not found_user.check_password(password):
                raise forms.ValidationError("Invalid email or password.")
                
        return cleaned_data