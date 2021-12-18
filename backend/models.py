from django.db import models
from django.db.models import fields
from django.db.models.deletion import CASCADE
from rest_framework import serializers

# Create your models here.
class Query(models.Model):
    query=models.CharField(max_length=1000)
    # videos=models.ManyToManyField(Video,related_name="queries")

class Video(models.Model):
    video_id=models.CharField(unique=True,max_length=15,blank=False)
    title=models.CharField(max_length=100,blank=False)
    description=models.CharField(max_length=5000)
    publishing_datetime=models.DateTimeField()
    # query=models.ManyToManyField(Query,related_name="videos")
    query=models.CharField(max_length=1000)


class Thumbnail_urls(models.Model):
    link=models.URLField()
    video=models.ForeignKey(Video,on_delete=CASCADE,related_name="thumbnails")

class Thumbnail_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Thumbnail_urls
        fields=['id','link']

class Video_Serializer(serializers.ModelSerializer):
    thumbnails=Thumbnail_Serializer(many = True)
    class Meta:
        model=Video
        fields=['id','video_id','title','description','publishing_datetime','thumbnails']

class Query_Serializer(serializers.ModelSerializer):
    videos=Video_Serializer(many = True)
    class Meta:
        model=Query
        fields=['id','query','videos']