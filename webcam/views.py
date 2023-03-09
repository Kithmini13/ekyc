from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_protect 
from webcam.camera import VideoCamera, gen
from webcam.liveness.face_anti_spoofing import Liveness
from webcam.liveness.server import offer
from aiohttp import web
import aiohttp
import json
import logging




def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                    content_type='multipart/x-mixed-replace; boundary=frame')

def index(request):
    # print("####### index() : ",request.body)
    # offer(request)
    return render(request, 'streamapp/index.html')

def face_match(request):
    return render(request, 'streamapp/face_match.html')

# @csrf_protect 
async def index_feed(request):
    print('####### index_feed :',request, type(request))
    params =  await request.json()
    sdp, type = offer(params)
    # return render(request, 'streamapp/index.html')
    logging.log("####### index_feed() : ",sdp, type)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": sdp, "type": type}
        ),
    )

def test(request):
    return render(request, 'streamapp/test.html')

def liveness(request):
    liveness = Liveness()
    liveness.process_video()

