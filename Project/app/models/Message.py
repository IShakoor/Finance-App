from django.db import models
from .user import CustomUser
from encrypted_model_fields.fields import EncryptedTextField

class Message(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=255)
    content = EncryptedTextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title