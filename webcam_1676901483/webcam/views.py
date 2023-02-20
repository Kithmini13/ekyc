from django.shortcuts import render
from django.http import StreamingHttpResponse
from webcam.camera import VideoCamera, gen

def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                    content_type='multipart/x-mixed-replace; boundary=frame')

def index(request):
    return render(request, 'streamapp/index.html')
