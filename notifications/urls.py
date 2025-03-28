from django.urls import path
from .views import notifications, mark_as_read

urlpatterns = [
    path('', notifications, name='notifications'),
    path('read/<int:pk>/', mark_as_read, name='mark_as_read'),
]
