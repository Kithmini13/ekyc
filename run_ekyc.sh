#!/bin/bash

# path to env
cd D:\\EKYC\\TEST\\webrtc

# activate env
source livenessenv379\\Scripts\\activate

# Start server
echo "Starting api service and ui access"
#python manage.py runserver 0.0.0.0:8000

# Start liveness server
echo "Starting liveness service on aiohttp"
cd D:\\EKYC\\TEST\\webcam-streaming\\liveness
python server.py --host 0.0.0.0 --port 8081

read -n1 -r -p "Press any key to exit..."