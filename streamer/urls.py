from django.urls import path
from . import views

urlpatterns = [
    path('add_rtsp_url/', views.add_rtsp_url, name='add_rtsp_url'),
]