from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('organizations/', include('organizations.urls')),
    path('notifications/', include('notifications.urls')),
    path('interviews/', include('interviews.urls')),
    path('chat/', include('chat.urls')),
    path('', views.index_dashboard, name='index_dashboard'),
    path('jobs/', include('jobs.urls')),
    path("__reload__/", include("django_browser_reload.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)