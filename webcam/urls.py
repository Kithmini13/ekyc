from django.urls import path, include
from webcam import views
from webcam.liveness.server import offer


urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('test/', views.test, name='test'),
    path('liveness/', views.liveness, name='liveness'),
    path('index_feed/', views.offer, name='index_feed'),
    path('face_match/', views.face_match, name='face_match'),
    ]