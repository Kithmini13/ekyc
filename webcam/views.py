from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from .models import Ekycvideo
from rest_framework.views import APIView
from .serializers import VideoPathSerializer
from rest_framework.response import Response
from rest_framework import status
from liveness.dbconn import dbquery
import datetime
import logging
import os

def index(request, usser_id):
    context = {
        'user_id': int(usser_id),
    }
    return render(request, 'index.html', context)

class VideoPathApiView(APIView):

    def get(self, request, *args, **kwargs):
        print('---------VideoPathView-----------------', settings.BASE_DIR)
        v_path = Ekycvideo.objects.all()
        serializer = VideoPathSerializer(v_path, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class DownloadVideo(APIView):
#     def get(self, request, reference_id, *args, **kwargs):
#         dbq = dbquery()
#         file_path = dbq.retrieve_data(reference_id)
#         success = 2

#         if os.path.exists(file_path):
#             with open(file_path, 'rb') as fh:
#                 response = HttpResponse(fh.read(), content_type="video/mp4")
#                 # response['Content-Disposition'] = 'attachment; filename=' + file_name
#                 return response
#         raise Http404

class DownloadVideo(APIView):
    def get(self, request, reference_id, *args, **kwargs):
        try:
            dbq = dbquery()
            file_path = dbq.retrieve_data(reference_id)

            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="video/mp4")
                    return response
            else:
                raise Http404("Video file not found.")

        except Exception as e:
            # Handle any other exceptions that might occur during the process
            return Response({"error": str(e)}, status=500)


# class SaveVideo(APIView):
#     def post(self, request, *args, **kwargs):
#         print('-----request----', request)
#         video_file = request.FILES.get('video')
#         user_id = request.POST.get('user_id')  # Retrieve the user_id from the request POST data
#         print('----video_file-----', type(video_file))
#         if video_file:
#             # unique_id = str(random.randint(1,100000))  # Generate a unique ID
#             file_name = f'recorded_video_{user_id}.mp4'  # Custom file name with UUID and MP4 extension
#             # file_path = '/opt/ml_hub/recorded_video/' + file_name # Specify the folder path where you want to save the video
#             file_path = '/home/seylanb/recorded_video/' + file_name
#             with open(file_path, 'wb') as file:
#                 for chunk in video_file.chunks():
#                     file.write(chunk)

#             dbq = dbquery()
#             dbq.insert_data(user_id=user_id, path=file_path, date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"))

#             return HttpResponse('Video saved successfully.')
#         return HttpResponse('Invalid request.')

# class SaveVideo(APIView):
#     def post(self, request, *args, **kwargs):
#         print('-----request----', request)
#         video_file = request.FILES.get('video')
#         user_id = request.POST.get('user_id')  # Retrieve the user_id from the request POST data
#         print('----video_file-----', type(video_file))
        
#         if video_file:
#             # unique_id = str(random.randint(1,100000))  # Generate a unique ID
#             file_name = f'recorded_video_{user_id}.mp4'  # Custom file name with UUID and MP4 extension
#             # file_path = '/opt/ml_hub/recorded_video/' + file_name # Specify the folder path where you want to save the video
#             file_path = '/home/seylanb/recorded_video/' + file_name
            
#             # Check if the directory is writable
#             if os.access('/home/seylanb/recorded_video/', os.W_OK):
#                 with open(file_path, 'wb') as file:
#                     for chunk in video_file.chunks():
#                         file.write(chunk)

#                 dbq = dbquery()
#                 dbq.insert_data(user_id=user_id, path=file_path, date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"))

#                 return HttpResponse('Video saved successfully.')
#             else:
#                 return HttpResponse('Error: No write access to the specified path.')
        
#         return HttpResponse('Invalid request.')

# class SaveVideo(APIView):
#     def post(self, request, *args, **kwargs):
#         # Configure the logging
#         logging.basicConfig(filename='server_log.txt', level=logging.DEBUG)

#         # Log the start of the function
#         logging.info('SaveVideo POST request received.')

#         video_file = request.FILES.get('video')
#         user_id = request.POST.get('user_id')
#         logging.info(f'User ID: {user_id}')

#         try:
#             if video_file:
#                 file_name = f'recorded_video_{user_id}.mp4'
#                 file_path = '/home/seylanb/recorded_video/' + file_name

#                 logging.info(f'Saving video to {file_path}')

#                 if os.access('/home/seylanb/recorded_video/', os.W_OK):
#                     with open(file_path, 'wb') as file:
#                         for chunk in video_file.chunks():
#                             file.write(chunk)

#                     dbq = dbquery()
#                     dbq.insert_data(user_id=user_id, path=file_path, date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"))

#                     logging.info('Video saved successfully.')
#                     return HttpResponse('Video saved successfully.')
#                 else:
#                     logging.error('Error: No write access to the specified path.')
#                     return HttpResponse('Error: No write access to the specified path.')
#         except Exception as e:
#             logging.error(f'Error: {str(e)}')
#             return HttpResponse(f'Error: {str(e)}')

class SaveVideo(APIView):
    def post(self, request, *args, **kwargs):
        logging.basicConfig(filename='server_log.txt', level=logging.DEBUG)
        logging.info('SaveVideo POST request received.')

        video_file = request.FILES.get('video')
        user_id = request.POST.get('user_id')
        logging.info(f'User ID: {user_id}')

        try:
            if video_file:
                file_name = f'recorded_video_{user_id}.mp4'
                file_path = '/home/seylanb/recorded_video/' + file_name
                logging.info(f'Saving video to {file_path}')

                if os.access('/home/seylanb/recorded_video/', os.W_OK):
                    # Save the resized video file
                    with open(file_path, 'wb') as file:
                        for chunk in video_file.chunks():
                            file.write(chunk)

                    # Insert data into the database
                    dbq = dbquery()
                    dbq.insert_data(user_id=user_id, path=file_path, date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"))

                    logging.info('Video saved successfully.')
                    return HttpResponse('Video saved successfully.')
                else:
                    logging.error('Error: No write access to the specified path.')
                    return HttpResponse('Error: No write access to the specified path.')
        except Exception as e:
            logging.error(f'Error: {str(e)}')
            return HttpResponse(f'Error: {str(e)}')


    
class SaveImage(APIView):
    def post(self, request, *args, **kwargs):
            try:
                image_file = request.FILES.get('image')
                user_id = request.POST.get('user_id')
                if image_file:
                    file_name = f'captured_image_{user_id}.jpg'
                    file_path = os.path.join('/home/seylanb/captured_images/', file_name)

                    with open(file_path, 'wb') as file:
                        for chunk in image_file.chunks():
                            file.write(chunk)

                    return JsonResponse({'message': 'Image saved successfully'}, status=200)
                else:
                    return JsonResponse({'message': 'Invalid request'}, status=400)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=500)
            
class RetrieveImage(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            file_name = f'captured_image_{user_id}.jpg'
            file_path = os.path.join('/home/seylanb/captured_images/', file_name)

            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='image/jpeg')
                response['Content-Disposition'] = f'inline; filename="{file_name}"'
                return response
        except Exception as e:
            return HttpResponse(str(e), status=500)
   


def your_view(request):
    logger = logging.getLogger(__name__)

    try:
        # Your code here
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")

        # Rest of your code
    except Exception as e:
        logger.exception("An exception occurred: %s", e)
