# accounts/models.py
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    codeforces_handle = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    rating = models.PositiveIntegerField(default=1500)
    max_rating = models.PositiveIntegerField(default=1500)

    def __str__(self):
        return self.user.username
