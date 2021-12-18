from django.db.models import query
from django.shortcuts import render
from backend.models import Query, Query_Serializer, Thumbnail_urls, Video, Video_Serializer
from django.http.response import JsonResponse
from django.utils.dateparse import parse_datetime
from googleapiclient.discovery import build
import datetime


DEVELOPER_KEY = 'AIzaSyCm86IhxgixQeIucWY10SDf85eA4NCbw8M'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=10,
        type='video'
    ).execute()
    # q=Query(query=query)
    # q.save()
    for item in search_response['items']:
        if len(Video.objects.filter(video_id=(item['id']['videoId'])))==1:
            continue
        if item['snippet']['description'][-3:]=="...":
            response=youtube.videos().list(
                id=item['id']['videoId'],
                part='snippet',
            ).execute()
            print(parse_datetime(response['items'][0]['snippet']['publishedAt']))
            video=Video(video_id=response['items'][0]['id'],title=response['items'][0]['snippet']['title'],description=response['items'][0]['snippet']['description'],publishing_datetime=parse_datetime(response['items'][0]['snippet']['publishedAt']),query=query)
        else:
            video=Video(video_id=item['id'],title=item['snippet']['title'],description=item['snippet']['description'],publishing_datetime=parse_datetime(item['snippet']['publishedAt']),query=query)
        video.save()
        for thumbnail in item['snippet']['thumbnails'].values():
            thumbnail_url=Thumbnail_urls(link=thumbnail['url'],video=video)
            thumbnail_url.save()
            video.thumbnails.add(thumbnail_url)
        # q.videos.add(video)

def index(request):
    return render(request,"backend/index.html")

def get_data(request):
    q=request.GET.get('q')
    if len(Video.objects.filter(query=q))>0:
        response=Video.objects.filter(query=q).order_by("-publishing_datetime")
        serializer=Video_Serializer(response,many = True)
        return JsonResponse(serializer.data,safe=False)
    else:
        youtube_search(q)
        response=Video.objects.filter(query=q).order_by("-publishing_datetime")
        serializer=Video_Serializer(response,many = True)
        return JsonResponse(serializer.data,safe=False)

def main():
    pass

if __name__=="main":
    main()