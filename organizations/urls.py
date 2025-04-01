from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.organization_register, name='organization_register'),
    path('login/', views.organization_login, name='organization_login'),
    path('logout/', views.organization_logout, name='organization_logout'),
    path('dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('dashboard/<int:org_id>/', views.organization_dashboard, name='organization_dashboard_specific'),

    # HR Management
    path('hr/add/', views.add_hr_staff, name='add_hr_staff'),
    path('hr/manage/', views.manage_hr_staff, name='manage_hr_staff'),
    path('hr/manage/<int:hr_id>/', views.manage_hr_staff, name='manage_hr_staff'),
    
    # Profile Management
    path('profile/', views.organization_profile_view, name='organization_profile_view'),
    path('profile/image/', views.organization_profile_image_update, name='organization_profile_image_update'),
    path('profile/banner/', views.organization_banner_image_update, name='organization_banner_image_update'),
    path('profile/details/', views.organization_details_update, name='organization_details_update'),
    
    # Job Applications
    path('<int:org_id>/applications/', views.manage_job_applications, name='manage_job_applications'),

        path('api/users/search/', views.user_search, name='user_search'),

]