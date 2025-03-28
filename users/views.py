from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from organizations.models import OrganizationHR
from .forms import ProfileImageForm, BannerImageForm, PersonalDetailsForm,SkillForm
from .models import Profile, Skill
from jobs.models import JobPosting  # Import JobPosting model

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Add this import

class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

def user_register(request):
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = EmailUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
    return render(request, 'users/login.html')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobs.models import JobPosting, JobApplication
from notifications.models import Notification
from interviews.models import Interview

@login_required
def user_dashboard(request):
    user = request.user
    job_postings = JobPosting.objects.all()
    user_applications = JobApplication.objects.filter(applicant=request.user)
    applied_jobs = {app.job.id: app.status for app in user_applications}
    interviews = Interview.objects.filter(job_application__applicant=user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Add this line to get HR organizations
    hr_organizations = OrganizationHR.objects.filter(user=request.user, is_active=True)
    
    return render(request, 'users/user_dashboard.html', {
        'job_postings': job_postings,
        'applied_jobs': applied_jobs,
        'interviews': interviews,
        'notifications': notifications,
        'hr_organizations': hr_organizations,  # Add this line
        'applications_count': user_applications.count(),
        'interviews_count': interviews.count(),
    })

def user_logout(request):
    logout(request)
    return redirect('index_dashboard')

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile_view.html', {'profile': profile})

@login_required
def profile_image_update(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = ProfileImageForm(instance=request.user.profile)
    return render(request, 'users/profile_image_update.html', {'form': form})

@login_required
def banner_image_update(request):
    if request.method == 'POST':
        form = BannerImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = BannerImageForm(instance=request.user.profile)
    return render(request, 'users/banner_image_update.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, Skill
from .forms import SkillSelectionForm

@login_required
def skills_select(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = SkillSelectionForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = SkillSelectionForm(instance=profile)
    
    all_skills = Skill.objects.all()  # Fetch all skills
    user_skills = profile.skills.all()  # Fetch user's current skills

    return render(request, 'users/skills_select.html', {
        'form': form,
        'all_skills': all_skills,
        'user_skills': user_skills
    })


@login_required
def skills_add(request):
    if request.method == 'POST':
        new_skill_name = request.POST.get('new_skill', '').strip()
        if new_skill_name:
            skill, created = Skill.objects.get_or_create(name=new_skill_name)
            profile = request.user.profile
            profile.skills.add(skill)
            profile.save()
            return redirect('skills_select')
    return render(request, 'users/skills_add.html')




@login_required
def personal_details_update(request):
    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = PersonalDetailsForm(instance=request.user.profile)
    return render(request, 'users/personal_details_update.html', {'form': form})



from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from jobs.models import JobApplication
from interviews.models import InterviewReview

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    applications = JobApplication.objects.filter(applicant=user)
    reviews = InterviewReview.objects.filter(interview__job_application__applicant=user)
    return render(request, 'users/user_profile.html', {
        'user_profile': user,
        'applications': applications,
        'reviews': reviews,
    })
