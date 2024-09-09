from django.db import models

from apps.users.models import User
from apps.utils.models import AbstractModel, TimeStampMixin


# Create your models here.
class Post(AbstractModel, TimeStampMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title


class Comment(AbstractModel, TimeStampMixin):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.text} - {self.author}"
