from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    age = models.IntegerField(default=0, null=True)
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=50, null=True)
    work = models.CharField(max_length=50, null=True)
    birthday = models.DateField('Birthday', null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Group(models.Model):
    name = models.CharField(max_length=50)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_admin')


class Post(models.Model):
    TIMELINE = 'T'
    GROUP = 'G'
    CHOICES = ((TIMELINE, 'TIMELINE'), (GROUP, 'GROUP'))

    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_owner")
    scope = models.CharField(max_length=1, choices=CHOICES, default=TIMELINE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='post_group', null=True)


class Comment(models.Model):
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')


class Like(models.Model):
    POST = 'P'
    COMMENT = 'C'
    CHOICES = ((POST, 'Post'), (COMMENT, 'Comment'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_user')
    scope = models.CharField(max_length=1, choices=CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='like_comment')

    def __str__(self):
        return "LIKE: " + self.user.first_name + " " + self.user.last_name


class CustomerGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_group')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_user')
