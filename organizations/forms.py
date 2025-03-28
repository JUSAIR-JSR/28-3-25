from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Organization, OrganizationHR

class OrganizationRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization_name = forms.CharField(max_length=255, required=True)
    registration_number = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['organization_name']
        if commit:
            user.save()
            Organization.objects.create(
                user=user,
                name=self.cleaned_data['organization_name'],
                registration_number=self.cleaned_data['registration_number']
            )
        return user

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import OrganizationHR

User = get_user_model()

class AddHRForm(forms.Form):
    user = forms.IntegerField(required=True, widget=forms.HiddenInput())
    username_display = forms.CharField(
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    role = forms.ChoiceField(choices=OrganizationHR.HR_ROLES, initial='RECRUITER')
    can_post_jobs = forms.BooleanField(required=False)
    can_manage_applications = forms.BooleanField(required=False)
    can_schedule_interviews = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

    def clean_user(self):
        user_id = self.cleaned_data['user']
        try:
            user = User.objects.get(id=user_id)
            if OrganizationHR.objects.filter(user=user, organization=self.organization).exists():
                raise ValidationError("This user is already an HR for your organization")
            return user
        except User.DoesNotExist:
            raise ValidationError("Please select a valid user from the dropdown")

    def save(self):
        return OrganizationHR.objects.create(
            user=self.cleaned_data['user'],
            organization=self.organization,
            role=self.cleaned_data['role'],
            can_post_jobs=self.cleaned_data['can_post_jobs'],
            can_manage_applications=self.cleaned_data['can_manage_applications'],
            can_schedule_interviews=self.cleaned_data['can_schedule_interviews'],
            added_by=self.request_user
        )
    

class EditHRForm(forms.ModelForm):  # New form for editing
    class Meta:
        model = OrganizationHR
        fields = ['role', 'can_post_jobs', 'can_manage_applications', 'can_schedule_interviews', 'is_active']
    

# Keep your existing image and details forms
class OrganizationProfileImageForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['profile_image']

class OrganizationBannerImageForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['banner_image']

class OrganizationDetailsForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'website', 'registration_number']