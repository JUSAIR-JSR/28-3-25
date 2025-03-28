from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import EditHRForm, OrganizationProfileImageForm, OrganizationBannerImageForm, OrganizationDetailsForm, OrganizationRegisterForm
from .models import Organization
from jobs.models import JobPosting
from jobs.forms import JobApplicationStatusForm
from django.contrib.auth import authenticate, login, logout
from jobs.models import JobApplication  # Correct import statement




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import (
    OrganizationRegisterForm, OrganizationProfileImageForm,
    OrganizationBannerImageForm, OrganizationDetailsForm, AddHRForm
)
from .models import Organization, OrganizationHR
from jobs.models import JobPosting, JobApplication
from interviews.models import Interview

def organization_register(request):
    if request.method == 'POST':
        form = OrganizationRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('organization_dashboard')
    else:
        form = OrganizationRegisterForm()
    return render(request, 'organizations/register.html', {'form': form})

@login_required
def organization_dashboard(request, org_id=None):
    """
    Organization dashboard view that handles both:
    - Main dashboard (no org_id)
    - Specific organization dashboard (with org_id)
    """
    # Initialize variables
    organization = None
    hr_role = None
    is_owner = False

    # Handle specific organization dashboard
    if org_id:
        organization = get_object_or_404(Organization, id=org_id)
        hr_role = OrganizationHR.objects.filter(
            user=request.user, 
            organization=organization, 
            is_active=True
        ).first()
        
        # Redirect if user has no access
        if not hr_role and request.user != organization.user:
            return redirect('index_dashboard')
            
        is_owner = (request.user == organization.user)

    # Handle main dashboard
    else:
        try:
            # Organization owner access
            organization = request.user.organization
            is_owner = True
        except Organization.DoesNotExist:
            # HR staff access
            hr_role = OrganizationHR.objects.filter(
                user=request.user, 
                is_active=True
            ).first()
            
            if not hr_role:
                return redirect('index_dashboard')
                
            organization = hr_role.organization

    # Set permissions
    hr_permissions = {
        'can_post_jobs': is_owner or (hr_role and hr_role.can_post_jobs),
        'can_manage_applications': is_owner or (hr_role and hr_role.can_manage_applications),
        'can_schedule_interviews': is_owner or (hr_role and hr_role.can_schedule_interviews)
    }

    # Get dashboard data
    job_postings = JobPosting.objects.filter(organization=organization)
    job_applications = JobApplication.objects.filter(job__organization=organization)
    interviews = Interview.objects.filter(job_application__job__organization=organization)

    # Prepare context
    context = {
        'organization': organization,
        'job_postings': job_postings,
        'job_applications': job_applications,
        'interviews': interviews,
        'is_owner': is_owner,
        'hr_permissions': hr_permissions,
        'hr_role': hr_role,
    }

    # Add HR staff list if owner
    if is_owner:
        context['hr_staff'] = OrganizationHR.objects.filter(
            organization=organization
        ).select_related('user')

    # Add HR organizations for dropdown (for HR staff)
    if not is_owner and hr_role:
        context['hr_organizations'] = OrganizationHR.objects.filter(
            user=request.user, 
            is_active=True
        ).select_related('organization')

    return render(request, 'organizations/organization_dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AddHRForm
from .models import Organization

@login_required
def add_hr_staff(request):
    organization = get_object_or_404(Organization, user=request.user)
    
    if request.method == 'POST':
        form = AddHRForm(
            request.POST, 
            organization=organization,
            request_user=request.user
        )
        if form.is_valid():
            try:
                hr = form.save()
                return redirect('manage_hr_staff')
            except Exception as e:
                form.add_error(None, f"Error saving HR record: {str(e)}")
    else:
        form = AddHRForm(organization=organization, request_user=request.user)
    
    return render(request, 'organizations/add_hr.html', {
        'form': form,
        'organization': organization
    })


@login_required
def manage_hr_staff(request, hr_id=None):
    organization = get_object_or_404(Organization, user=request.user)
    
    if hr_id:
        hr = get_object_or_404(OrganizationHR, id=hr_id, organization=organization)
        
        if request.method == 'POST':
            if 'toggle_active' in request.POST:
                hr.is_active = not hr.is_active
                hr.save()
                return redirect('manage_hr_staff')
            else:
                form = EditHRForm(request.POST, instance=hr)  # Use EditHRForm here
                if form.is_valid():
                    form.save()
                    return redirect('manage_hr_staff')
        else:
            form = EditHRForm(instance=hr)  # Use EditHRForm here
        
        return render(request, 'organizations/edit_hr.html', {
            'form': form,
            'hr': hr,
            'organization': organization
        })
    
    hr_staff = OrganizationHR.objects.filter(organization=organization)
    return render(request, 'organizations/manage_hr.html', {
        'hr_staff': hr_staff,
        'organization': organization
    })

# Keep all your existing profile and image update views
# ... (organization_profile_view, organization_profile_image_update, etc.)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from jobs.models import JobApplication  # Correct import statement
from jobs.forms import JobApplicationStatusForm  # Correct import statement
from notifications.models import Notification

@login_required
def manage_job_applications(request, org_id=None):
    # Get the organization - either from URL or user's default
    if org_id:
        organization = get_object_or_404(Organization, id=org_id)
        # Verify HR has permissions for this org
        hr_role = OrganizationHR.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
            can_manage_applications=True
        ).first()
        if not hr_role and request.user != organization.user:
            return redirect('index_dashboard')
    else:
        try:
            # Organization owner access
            organization = request.user.organization
        except Organization.DoesNotExist:
            # HR staff access - get first organization they have permissions for
            hr_role = OrganizationHR.objects.filter(
                user=request.user,
                is_active=True,
                can_manage_applications=True
            ).first()
            if not hr_role:
                return redirect('index_dashboard')
            organization = hr_role.organization

    # Get applications for this organization
    job_applications = JobApplication.objects.filter(
        job__organization=organization
    ).select_related('job', 'applicant')

    if request.method == 'POST':
        form = JobApplicationStatusForm(request.POST)
        if form.is_valid():
            application = get_object_or_404(JobApplication, 
                pk=request.POST.get('application_id'),
                job__organization=organization
            )
            application.status = form.cleaned_data['status']
            application.save()

            Notification.objects.create(
                user=application.applicant,
                message=f"Your application status for {application.job.title} has been updated to {application.status}."
            )
            return redirect('manage_job_applications', org_id=organization.id)
    else:
        form = JobApplicationStatusForm()

    return render(request, 'organizations/manage_job_applications.html', {
        'organization': organization,
        'job_applications': job_applications,
        'form': form,
        'is_owner': request.user == organization.user
    })


def organization_login(request):
    if request.method == 'POST':
        organization_name = request.POST['organization_name']
        password = request.POST['password']
        user = authenticate(request, username=organization_name, password=password)
        if user is not None:
            login(request, user)
            return redirect('organization_dashboard')
    return render(request, 'organizations/login.html')



def organization_logout(request):
    logout(request)
    return redirect('index_dashboard')

@login_required
def organization_profile_view(request):
    organization, created = Organization.objects.get_or_create(user=request.user)
    return render(request, 'organizations/profile_view.html', {'organization': organization})

@login_required
def organization_profile_image_update(request):
    if request.method == 'POST':
        form = OrganizationProfileImageForm(request.POST, request.FILES, instance=request.user.organization)
        if form.is_valid():
            form.save()
            return redirect('organization_profile_view')
    else:
        form = OrganizationProfileImageForm(instance=request.user.organization)
    return render(request, 'organizations/profile_image_update.html', {'form': form})

@login_required
def organization_banner_image_update(request):
    if request.method == 'POST':
        form = OrganizationBannerImageForm(request.POST, request.FILES, instance=request.user.organization)
        if form.is_valid():
            form.save()
            return redirect('organization_profile_view')
    else:
        form = OrganizationBannerImageForm(instance=request.user.organization)
    return render(request, 'organizations/banner_image_update.html', {'form': form})

@login_required
def organization_details_update(request):
    if request.method == 'POST':
        form = OrganizationDetailsForm(request.POST, request.FILES, instance=request.user.organization)
        if form.is_valid():
            form.save()
            return redirect('organization_profile_view')
    else:
        form = OrganizationDetailsForm(instance=request.user.organization)
    return render(request, 'organizations/details_update.html', {'form': form})



from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def user_search(request):
    query = request.GET.get('term', '')
    users = User.objects.filter(username__icontains=query)[:10]
    results = [{'id': user.id, 'text': user.username} for user in users]
    return JsonResponse({'results': results})

from django.db.models import Count
@login_required
def hr_dashboard(request, org_id=None):
    """
    HR-specific dashboard that:
    - Shows only organizations the HR has access to
    - Strictly isolates data per organization
    - Provides organization switching
    """
    # Get all active HR roles for this user
    hr_roles = OrganizationHR.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('organization')
    
    # If no HR roles, redirect (shouldn't normally happen as decorator should prevent)
    if not hr_roles.exists():
        return redirect('index_dashboard')

    # If no org_id specified, redirect to first organization
    if not org_id:
        return redirect('hr_dashboard', org_id=hr_roles.first().organization.id)

    # Get current organization and verify access
    current_org = get_object_or_404(Organization, id=org_id)
    current_hr_role = hr_roles.filter(organization=current_org).first()
    
    # If no access to requested org, redirect to first available
    if not current_hr_role:
        return redirect('hr_dashboard', org_id=hr_roles.first().organization.id)

    # Get organization-specific data with strict filtering
    job_postings = JobPosting.objects.filter(
        organization=current_org
    ).order_by('-posted_on')
    
    applications = JobApplication.objects.none()
    if current_hr_role.can_manage_applications:
        applications = JobApplication.objects.filter(
            job__organization=current_org
        ).select_related('job', 'applicant')
    
    interviews = Interview.objects.none()
    if current_hr_role.can_schedule_interviews:
        interviews = Interview.objects.filter(
            job_application__job__organization=current_org
        ).select_related('job_application')

    context = {
        # Organization info
        'current_org': current_org,
        'hr_organizations': [hr.organization for hr in hr_roles],
        
        # HR role and permissions
        'hr_role': current_hr_role,
        'can_post_jobs': current_hr_role.can_post_jobs,
        'can_manage_applications': current_hr_role.can_manage_applications,
        'can_schedule_interviews': current_hr_role.can_schedule_interviews,
        
        # Organization data
        'job_postings': job_postings,
        'applications': applications,
        'interviews': interviews,
        
        # UI helpers
        'is_hr': True,
        'is_owner': False,  # HR dashboard is never for owners
    }
    
    return render(request, 'organizations/hr_dashboard.html', context)