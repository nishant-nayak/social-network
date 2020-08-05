from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.TextField(max_length=280)
    time = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_users", blank=True)

    def serialize(self, request):
        return {
            "id": self.id,
            "username": self.user.username,
            "text": self.text,
            "time": self.time.strftime('%b %#d %Y, %#I:%M %p'),
            "likes": self.likes.count(),
            "is_liked": self.likes.filter(username=request.user.username).exists()
        }

class Follower(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey('User', on_delete=models.CASCADE, related_name="following")

class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.TextField(max_length=280)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)