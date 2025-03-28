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

@login_required
def job_posting_detail(request, org_id, pk):
    organization = get_object_or_404(Organization, id=org_id)
    job_posting = get_object_or_404(JobPosting, pk=pk, organization=organization)
    applications = JobApplication.objects.filter(job=job_posting)
    
    # Check if user has permission to manage applications
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

    if can_manage:
        if request.method == 'POST':
            form = JobApplicationStatusForm(request.POST)
            if form.is_valid():
                application = get_object_or_404(JobApplication, pk=request.POST.get('application_id'))
                application.status = form.cleaned_data['status']
                application.save()

                Notification.objects.create(
                    user=application.applicant,
                    message=f"Your application status for {application.job.title} has been updated to {application.status}."
                )

                return redirect('job_posting_detail', org_id=org_id, pk=pk)
        else:
            form = JobApplicationStatusForm()
        
        return render(request, 'jobs/job_posting_detail.html', {
            'job_posting': job_posting,
            'applications': applications,
            'form': form,
            'organization': organization,
            'can_manage': can_manage
        })
    
    return render(request, 'jobs/job_posting_detail.html', {
        'job_posting': job_posting,
        'applications': applications,
        'organization': organization,
        'can_manage': can_manage
    })