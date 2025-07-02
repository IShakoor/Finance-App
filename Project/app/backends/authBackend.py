from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# allow login with encrypted email
class EncryptedEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        email = kwargs.get('email', username)

        # loop through users & find matching email
        try:
            for user in UserModel.objects.all():
                if user.email == email and user.check_password(password):
                    return user
        except UserModel.DoesNotExist:
            return None
