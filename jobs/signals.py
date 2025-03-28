from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobPosting
from users.models import Profile
from notifications.models import Notification

@receiver(post_save, sender=JobPosting)
def notify_users_about_new_job(sender, instance, created, **kwargs):
    if created:
        required_skills_ids = list(instance.required_skills.values_list('id', flat=True))
        users = Profile.objects.filter(skills__id__in=required_skills_ids).distinct()
        for profile in users:
            Notification.objects.create(
                user=profile.user,
                message=f"A new job posting matches your skills: {instance.title}."
            )
