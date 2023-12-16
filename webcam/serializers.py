# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import Ekycvideo

class VideoPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ekycvideo
        fields = ["id", "user_id", "path", "date_time"]