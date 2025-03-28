from django import forms
from .models import Profile, Skill

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']

class BannerImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['banner_image']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['certifications', 'qualifications', 'location']

class SkillSelectionForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Profile
        fields = ['skills']

