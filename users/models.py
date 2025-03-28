from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='banner_images/', blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
