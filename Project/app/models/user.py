from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedTextField

# Class to manage users and superusers
# - Allow for user details to be entered and validated
# - Create new user
# - Save the user to the database
class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        
        # Validate email
        if not email:
            raise ValueError(_("The Email field must be set"))
        if '@' not in email:
            raise ValueError(_("Invalid email format"))
        email = self.normalize_email(email)

        # Set default values for custom fields if not already provided
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)

        # Create the user and save to the database
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):

        # Set the extra fields to default values
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Validate superuser requirements
        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if not password:
            raise ValueError(_('Superuser must have a password.'))

        return self.create_user(username, email, password, **extra_fields)

# Defining User class
# - Accepts user inputs
# - Sets required fields
class CustomUser(AbstractBaseUser, PermissionsMixin):

    # User data
    username = EncryptedTextField(_("Username"), max_length=150, unique=True)
    email = EncryptedTextField(_("Email Address"), unique=True)
    password = models.CharField(_("Password"), max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    plaid_access_token = EncryptedTextField(max_length=255, null=True, blank=True)

    # Custom manager
    objects = CustomUserManager()

    # Required fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

