from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField()
    registration_number = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='banner_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Keep only auto_now_add
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationHR(models.Model):
    HR_ROLES = [
        ('RECRUITER', 'Recruiter'),
        ('MANAGER', 'HR Manager'),
        ('ADMIN', 'HR Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hr_roles')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='hr_members')
    role = models.CharField(max_length=20, choices=HR_ROLES, default='RECRUITER')
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_hrs')
    added_at = models.DateTimeField(auto_now_add=True)
    can_post_jobs = models.BooleanField(default=False)
    can_manage_applications = models.BooleanField(default=False)
    can_schedule_interviews = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'organization')
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"

    def clean(self):
        # Prevent adding organization owner as HR
        if self.user == self.organization.user:
            raise ValidationError("Organization owner cannot be added as HR staff")