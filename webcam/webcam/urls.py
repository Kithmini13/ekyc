from django.urls import path, include
from webcam import views


urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),  #laptop camera
    path('webcam_feed/', views.webcam_feed, name='webcam_feed'),   #phone camera
    ]