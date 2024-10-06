from django.db import models

from apps.users.models import User
from apps.utils.models import AbstractModel, TimeStampMixin


# Create your models here.
class Tag(AbstractModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(AbstractModel, TimeStampMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', db_index=True)
    tags = models.ManyToManyField(Tag, through='PostTag', blank=True)

    def __str__(self):
        return self.title


class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, db_index=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_index=True)


class Comment(AbstractModel, TimeStampMixin):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', db_index=True)

    def __str__(self):
        return f"{self.text} - {self.author}"
