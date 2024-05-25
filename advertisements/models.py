from django.db import models
from users.models import User
import uuid


class Advertisement(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=300)
    content = models.TextField(max_length=5000)

    def __str__(self):
        return self.title