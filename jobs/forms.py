from django import forms
from .models import JobPosting, Skill

class JobPostingForm(forms.ModelForm):
    application_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    required_skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    new_skills = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter new skills separated by commas")
    
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'required_qualifications', 'required_skills', 'new_skills', 'location', 'application_deadline', 'job_post_image']



from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = []  # No fields shown to the user
    cv = forms.FileField()  # Add a field for uploading CV



from django import forms
from .models import JobApplication

class JobApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status']
