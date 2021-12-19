from django.shortcuts import render
from backend.models import  Thumbnail_urls, Video, Video_Serializer
from django.http.response import HttpResponseRedirect, JsonResponse
from django.utils.dateparse import parse_datetime
from django.core.paginator import Paginator
from googleapiclient.discovery import build
from django.urls import reverse
import math,threading,asyncio


DEVELOPER_KEY = '<Your API Key here>'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    try:
        search_response = youtube.search().list(
            q="football",
            part='id,snippet',
            maxResults=50, # getting the most recent 50 videos and saving them in the database
            type='video'
        ).execute()
    except:
        return 403
    print(search_response)
    for item in search_response['items']:
        if len(Video.objects.filter(video_id=(item['id']['videoId'])))==1:
            continue
        if item['snippet']['description'][-3:]=="...":
            response=youtube.videos().list(
                id=item['id']['videoId'],
                part='snippet',
            ).execute()
            video=Video(video_id=response['items'][0]['id'],title=response['items'][0]['snippet']['title'],description=response['items'][0]['snippet']['description'],publishing_datetime=parse_datetime(response['items'][0]['snippet']['publishedAt']))
        else:
            video=Video(video_id=item['id']['videoId'],title=item['snippet']['title'],description=item['snippet']['description'],publishing_datetime=parse_datetime(item['snippet']['publishedAt']))
        video.save()
        for thumbnail in item['snippet']['thumbnails'].values():
            thumbnail_url=Thumbnail_urls(link=thumbnail['url'],video=video)
            thumbnail_url.save()
            video.thumbnails.add(thumbnail_url)
    return 200

def index(request):
    return render(request,"backend/index.html")

def get_data(request):
    start=1
    order="publishing_datetime"
    maxResults=10
    publishedAfter=None
    if 'start' in request.GET:
        start=request.GET.get('start')
    if 'order' in request.GET:
        order=request.GET.get('order')
    if 'maxResults' in request.GET:
        maxResults=request.GET.get('maxResults')
    if 'publishedAfter' in request.GET:
        publishedAfter=parse_datetime(request.GET.get('publishedAfter'))
    code=youtube_search()
    if code==403:
        return JsonResponse({"error":"Quota Exhausted for provided API key."})
    if publishedAfter is not None:
        videos=Video.objects.filter(publishing_datetime__gte=publishedAfter).order_by(f"-{order}").all()
    else:
        videos=Video.objects.all().order_by(f"-{order}").all()
    paginator=Paginator(videos,maxResults)
    page_no=math.ceil(int(start)/10)
    page_obj=paginator.get_page(page_no)
    videos=[video for video in page_obj]
    serializer=Video_Serializer(videos,many = True)
    return JsonResponse({"videos":serializer.data,"num_pages":paginator.num_pages})


