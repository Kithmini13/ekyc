#from webcam.camera import VideoCamera, gen

from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from webcam.camera import VideoCamera, IPWebCam
# Create your views here.


def index(request):
	return render(request, 'streamapp/index.html')


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
	return StreamingHttpResponse(gen(IPWebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')