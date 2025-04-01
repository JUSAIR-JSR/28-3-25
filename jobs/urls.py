from django.urls import path

from jobs import views
from .views import job_posting_list, job_posting_detail, job_posting_create, job_posting_update, job_posting_delete, job_application_create, job_application_success, user_job_applications

urlpatterns = [
    path('<int:org_id>/', views.job_posting_list, name='job_posting_list'),
    path('<int:org_id>/create/', views.job_posting_create, name='job_posting_create'),
    path('<int:org_id>/<int:pk>/', views.job_posting_detail, name='job_posting_detail'),
    path('<int:org_id>/<int:pk>/edit/', views.job_posting_update, name='job_posting_update'),
    path('<int:org_id>/<int:pk>/delete/', views.job_posting_delete, name='job_posting_delete'),
    path('<int:org_id>/<int:pk>/apply/', views.job_application_create, name='job_application_create'),
    path('application/success/', job_application_success, name='job_application_success'),
    path('applications/', user_job_applications, name='user_job_applications'),

    path('organization-jobs/<int:org_id>/', views.job_posting_org_view, name='job_posting_org_view'),
]
