from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobPosting, JobApplication, Skill
from .forms import JobPostingForm, JobApplicationForm, JobApplicationStatusForm
from notifications.models import Notification
from users.models import Profile
from organizations.models import Organization, OrganizationHR

@login_required
def user_job_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user)
    return render(request, 'jobs/job_application_list.html', {'applications': applications})

@login_required
def job_posting_list(request, org_id=None):
    # Get the organization
    if org_id:
        organization = get_object_or_404(Organization, id=org_id)
        # Verify HR has permissions for this org
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).first()
        if not hr_role and request.user != organization.user:
            return redirect('index_dashboard')
    else:
        # For organization owners
        try:
            organization = request.user.organization
        except Organization.DoesNotExist:
            return redirect('index_dashboard')

    job_postings = JobPosting.objects.filter(organization=organization)
    return render(request, 'jobs/job_posting_list.html', {
        'job_postings': job_postings,
        'organization': organization
    })

@login_required
def job_posting_create(request, org_id=None):
    # Get the organization
    if org_id:
        organization = get_object_or_404(Organization, id=org_id)
        # Verify HR has permissions for this org
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_post_jobs=True
        ).first()
        if not hr_role and request.user != organization.user:
            return redirect('index_dashboard')
    else:
        # For organization owners
        try:
            organization = request.user.organization
        except Organization.DoesNotExist:
            return redirect('index_dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.organization = organization
            job_posting.posted_by = request.user  # Track which HR created this
            job_posting.save()
            form.save_m2m()

            # Handle new skills
            new_skills = form.cleaned_data['new_skills']
            if new_skills:
                for skill_name in [s.strip() for s in new_skills.split(',')]:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job_posting.required_skills.add(skill)

            # Create notifications for users with matching skills
            required_skills_ids = job_posting.required_skills.values_list('id', flat=True)
            users = Profile.objects.filter(skills__id__in=required_skills_ids).distinct()
            for profile in users:
                matching_skills = profile.skills.filter(id__in=required_skills_ids)
                skill_names = ", ".join([skill.name for skill in matching_skills])
                Notification.objects.create(
                    user=profile.user,
                    message=f"A new job posting matches your skills: {job_posting.title}. Matching skills: {skill_names}."
                )

            return redirect('organization_dashboard_specific', org_id=organization.id)
    else:
        form = JobPostingForm()
    
    return render(request, 'jobs/job_posting_create.html', {
        'form': form,
        'organization': organization
    })

@login_required
def job_posting_update(request, org_id, pk):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, pk=pk, organization=organization)
    
    # Verify permissions
    if request.user != organization.user:
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_post_jobs=True
        ).first()
        if not (request.user == organization.user or 
           (hr_role and job_posting.posted_by == request.user)):
            return redirect('index_dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES, instance=job_posting)
        if form.is_valid():
            job_posting = form.save()
            
            # Handle new skills
            new_skills = form.cleaned_data['new_skills']
            if new_skills:
                for skill_name in [s.strip() for s in new_skills.split(',')]:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job_posting.required_skills.add(skill)

            return redirect('organization_dashboard_specific', org_id=organization.id)
    else:
        form = JobPostingForm(instance=job_posting)
    
    return render(request, 'jobs/job_posting_update.html', {
        'form': form,
        'organization': organization,
        'job_posting': job_posting
    })

@login_required
def job_posting_delete(request, org_id, pk):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, pk=pk, organization=organization)
    
    # Verify permissions
    if request.user != organization.user:
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_post_jobs=True
        ).first()
        if not hr_role:
            return redirect('index_dashboard')

    if request.method == 'POST':
        job_posting.delete()
        return redirect('organization_dashboard_specific', org_id=organization.id)
    
    return render(request, 'jobs/job_posting_delete.html', {
        'job_posting': job_posting,
        'organization': organization
    })

@login_required
def job_application_create(request, org_id, pk):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, pk=pk, organization=organization)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job_application = form.save(commit=False)
            job_application.job = job_posting
            job_application.applicant = request.user
            job_application.cv = request.FILES['cv']
            job_application.save()

            # Create a notification for the organization
            Notification.objects.create(
                user=job_posting.organization.user,
                message=f"{request.user.username} has applied for {job_posting.title}"
            )

            return redirect('job_application_success')
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/job_application_create.html', {
        'form': form,
        'job_posting': job_posting,
        'organization': organization
    })

def job_application_success(request):
    return render(request, 'jobs/job_application_success.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from interviews.models import Interview
from interviews.forms import InterviewForm
from jobs.models import JobPosting, JobApplication
from organizations.models import Organization

@login_required
def job_posting_detail(request, org_id, pk):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, pk=pk, organization=organization)
    applications = JobApplication.objects.filter(job=job_posting)

    # Check if user has permission to manage applications and interviews
    can_manage = False
    if request.user == organization.user:
        can_manage = True
    else:
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_manage_applications=True
        ).first()
        if hr_role:
            can_manage = True

    form = None  # Initialize the form outside the if conditions to ensure it always exists

    if can_manage:
        if request.method == 'POST':
            # Handle status update
            if 'update_status' in request.POST:
                application = get_object_or_404(JobApplication, id=request.POST['application_id'])
                application.status = request.POST.get('status')
                application.save()
                return redirect('job_posting_detail', org_id=org_id, pk=pk)

            # Handle creating or updating an interview
            if 'create_interview' in request.POST:
                job_application = get_object_or_404(JobApplication, id=request.POST.get('application_id'))
                form = InterviewForm(request.POST)
                if form.is_valid():
                    interview = form.save(commit=False)
                    interview.job_application = job_application
                    interview.save()  # Save the interview

                    # Add a success message (optional)
                    return redirect('job_posting_detail', org_id=org_id, pk=pk)

            # Handle interview update or deletion
            if 'update_interview' in request.POST:
                interview = get_object_or_404(Interview, id=request.POST['interview_id'])
                return redirect('update_interview', interview_id=interview.id)
            elif 'delete_interview' in request.POST:
                interview = get_object_or_404(Interview, id=request.POST['interview_id'])
                interview.delete()
                return redirect('job_posting_detail', org_id=org_id, pk=pk)

        else:
            form = InterviewForm()  # If GET request, initialize form here

    return render(request, 'jobs/job_posting_detail.html', {
        'job_posting': job_posting,
        'applications': applications,
        'organization': organization,
        'can_manage': can_manage,
        'form': form if can_manage else None
    })




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from organizations.models import Organization, OrganizationHR
from jobs.models import JobPosting  # Import JobPosting model

@login_required
def job_posting_org_view(request, org_id=None):
    # Get the current organization
    if org_id:
        current_org = get_object_or_404(Organization, id=org_id)
        # Verify HR has access to this org
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=current_org,
            is_active=True
        ).first()
        if not hr_role and request.user != current_org.user:
            return redirect('index_dashboard')
    else:
        # For organization owners
        try:
            current_org = request.user.organization
        except Organization.DoesNotExist:
            # For HR staff - get their first assigned organization
            hr_role = OrganizationHR.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            if not hr_role:
                return redirect('index_dashboard')
            current_org = hr_role.organization

    # Check if the user is the organization owner
    is_owner = request.user == current_org.user

    # If the user is the owner, they can see all job postings from the organization
    if is_owner:
        job_postings = JobPosting.objects.filter(organization=current_org).select_related('posted_by')
    else:
        # If the user is HR, show only jobs posted by them
        job_postings = JobPosting.objects.filter(
            organization=current_org,
            posted_by=request.user
        ).select_related('posted_by')

    # Get all organizations this HR user has access to (for switcher)
    hr_organizations = OrganizationHR.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('organization')

    return render(request, 'jobs/job_posting_org_view.html', {
        'job_postings': job_postings,
        'current_org': current_org,
        'hr_roles': hr_organizations,  # Changed from hr_organizations to hr_roles
        'is_owner': is_owner
    })




from django.shortcuts import render, get_object_or_404
from .models import JobApplication

def job_application_detail(request, pk):
    job_application = get_object_or_404(JobApplication, pk=pk)
    return render(request, 'jobs/job_application_detail.html', {'job_application': job_application})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from interviews.models import Interview
from interviews.forms import InterviewForm
from jobs.models import JobPosting, JobApplication
from organizations.models import Organization

@login_required
def manage_interview(request, org_id, job_id, application_id, interview_id=None):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, id=job_id, organization=organization)
    job_application = get_object_or_404(JobApplication, id=application_id, job=job_posting)

    # Check if user has permission to manage interviews
    can_manage = False
    if request.user == organization.user:
        can_manage = True
    else:
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_manage_applications=True
        ).first()
        if hr_role:
            can_manage = True

    if not can_manage:
        return redirect('job_posting_detail', org_id=org_id, pk=job_id)

    if interview_id:  # Update an existing interview
        interview = get_object_or_404(Interview, id=interview_id)
        form = InterviewForm(request.POST or None, instance=interview)
    else:  # Create a new interview
        form = InterviewForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        interview = form.save(commit=False)
        interview.job_application = job_application
        interview.save()
        return redirect('job_posting_detail', org_id=org_id, pk=job_id)

    return render(request, 'jobs/manage_interview.html', {
        'job_posting': job_posting,
        'job_application': job_application,
        'form': form,
        'interview': interview if interview_id else None
    })
