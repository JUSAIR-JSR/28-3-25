from django import forms
from .models import Interview, ReviewQuestion, InterviewReview
from jobs.models import JobApplication

class InterviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        if organization:
            self.fields['job_application'].queryset = JobApplication.objects.filter(job__organization=organization)

    class Meta:
        model = Interview
        fields = ['job_application', 'scheduled_time', 'interview_link']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ReviewQuestionForm(forms.ModelForm):
    class Meta:
        model = ReviewQuestion
        fields = ['question_text']

class InterviewReviewForm(forms.ModelForm):
    class Meta:
        model = InterviewReview
        fields = ['question', 'rating',]
