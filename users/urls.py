from django.urls import path
from .views import user_register, user_login, user_dashboard, user_logout, profile_view, profile_image_update, banner_image_update, personal_details_update, skills_select, skills_add, user_profile

urlpatterns = [
    path('register/', user_register, name='user_register'),
    path('login/', user_login, name='user_login'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('logout/', user_logout, name='user_logout'),
    path('profile/view/', profile_view, name='profile_view'),
    path('profile/update/image/', profile_image_update, name='profile_image_update'),
    path('profile/update/banner/', banner_image_update, name='banner_image_update'),
    path('profile/update/details/', personal_details_update, name='personal_details_update'),
    path('skills/select/', skills_select, name='skills_select'),  # Updated URL for selecting skills
    path('skills/add/', skills_add, name='skills_add'),  # Updated URL for adding new skills
    path('profile/<str:username>/', user_profile, name='user_profile'),
]
