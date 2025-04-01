from django.db import models
from django.contrib.auth.models import User
from organizations.models import Organization

class Skill(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

from django.db import models
from organizations.models import Organization
from users.models import Skill  # Import Skill model from users app

class JobPosting(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_qualifications = models.TextField()
    required_skills = models.ManyToManyField(Skill, blank=True)  # Use the same Skill model
    location = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateTimeField()
    job_post_image = models.ImageField(upload_to='job_images/', blank=True, null=True)
    posted_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='posted_jobs')

    def save(self, *args, **kwargs):
        if self.posted_by is None:  # Only set if not assigned
            self.posted_by = self.organization.user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offer_made', 'Offer Made'),
    ])
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)


    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"