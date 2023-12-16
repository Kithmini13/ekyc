# Create your models here.
from django.db import models

# Create your models here.
class Ekycvideo(models.Model):
    user_id=models.CharField(max_length=100)
    path=models.TextField()
    date_time=models.DateTimeField()
    def __str__(self):
        return self.user_id

    class Meta:
        db_table = 'video_info'
