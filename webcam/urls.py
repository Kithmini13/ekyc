from django.urls import path, include
from webcam import views
from .views import RetrieveImage, SaveImage, VideoPathApiView, DownloadVideo, SaveVideo

from django.urls import path
from . import views

app_name = 'webcam'

urlpatterns = [
    path('<int:usser_id>/', views.index, name='index'),  # Update the URL pattern with a reference ID capture
    path('video_path/', VideoPathApiView.as_view()),
    path('download/<int:reference_id>/', DownloadVideo.as_view()),
    path('save_video/',SaveVideo.as_view()),
    path('save_image/', SaveImage.as_view(), name='save_image'),
    path('retrieve_image/<str:user_id>/', RetrieveImage.as_view(), name='retrieve_image'),
    ]

