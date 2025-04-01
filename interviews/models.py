from django.db import models
from jobs.models import JobApplication

class Interview(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    scheduled_time = models.DateTimeField()
    interview_link = models.URLField()

class ReviewQuestion(models.Model):
    question_text = models.TextField()
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)



class InterviewReview(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='reviews')
    question = models.ForeignKey(ReviewQuestion, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True, choices=[(i, f"{i}/10") for i in range(11)])  # Rating between 0 and 10
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.interview} - {self.rating}/10"

