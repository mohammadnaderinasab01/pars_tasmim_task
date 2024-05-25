from django.db import models
import uuid
from users.models import User
from advertisements.models import Advertisement


class Comment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    content = models.TextField()
    # user_id = models.CharField(max_length=300)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    advertisement_id = models.ForeignKey(Advertisement, on_delete=models.CASCADE, null=True, blank=True)
    comment_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content