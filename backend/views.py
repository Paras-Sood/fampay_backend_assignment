from django.shortcuts import render
from backend.models import  Thumbnail_urls, Video, Video_Serializer
from django.http.response import JsonResponse
from django.utils.dateparse import parse_datetime
from django.core.paginator import Paginator
from googleapiclient.discovery import build
import math,threading

API_KEY = '' # Your API key here
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()


def youtube_search(maxResults=50):
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=API_KEY)
        latest_video=Video.objects.order_by("-publishing_datetime").first()
        if latest_video is not None:
            last_publishing_datetime=latest_video.publishing_datetime.isoformat()
        else:
            last_publishing_datetime=None
        search_response = youtube.search().list(
            q="football",
            part='id,snippet',
            maxResults=maxResults, # getting the most recent 50 videos for the first time and saving them in the database
            type='video',
            publishedAfter=last_publishing_datetime, # Getting new videos which have been published after the latest stored video in the database
        ).execute()
    except:
        error_message="Quota Exhausted on provided API keys."
        print(error_message)
        return
    for item in search_response['items']:
        if len(Video.objects.filter(video_id=(item['id']['videoId'])))==1: # if this video is already present in the databse then no need to add it again
            continue
        if item['snippet']['description'][-3:]=="...":
            response=youtube.videos().list(
                id=item['id']['videoId'],
                part='snippet',
            ).execute() # Getting complete description
            video=Video(video_id=response['items'][0]['id'],title=response['items'][0]['snippet']['title'],description=response['items'][0]['snippet']['description'],publishing_datetime=parse_datetime(response['items'][0]['snippet']['publishedAt']))
        else:
            video=Video(video_id=item['id']['videoId'],title=item['snippet']['title'],description=item['snippet']['description'],publishing_datetime=parse_datetime(item['snippet']['publishedAt']))
        video.save()
        for thumbnail in item['snippet']['thumbnails'].values():
            thumbnail_url=Thumbnail_urls(link=thumbnail['url'],video=video)
            thumbnail_url.save()
            video.thumbnails.add(thumbnail_url)

def index(request):
    youtube_search()
    event = threading.Event()
    a = ThreadJob(youtube_search,event,10)
    a.start()
    return render(request,"backend/index.html")

def get_data(request):
    if API_KEY=="":
        return JsonResponse({"error":"Provide an API Key"})
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
    if publishedAfter is not None:
        videos=Video.objects.filter(publishing_datetime__gte=publishedAfter).order_by(f"-{order}")
    else:
        videos=Video.objects.all().order_by(f"-{order}")
    paginator=Paginator(videos,maxResults)
    page_no=math.ceil(int(start)/10)
    page_obj=paginator.get_page(page_no)
    videos=page_obj.object_list
    serializer=Video_Serializer(videos,many = True)
    return JsonResponse({"videos":serializer.data,"num_pages":paginator.num_pages})


