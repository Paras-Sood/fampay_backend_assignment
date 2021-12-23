from django.shortcuts import render
from backend.models import  Thumbnail_urls, Video, Video_Serializer
from django.http.response import JsonResponse
from django.utils.dateparse import parse_datetime
from django.core.paginator import Paginator
from googleapiclient.discovery import build
import math,threading

API_KEYS_LIST = [] # Your API keys here (Provide as string Eg - ['a','b','c'])
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

class API_KEYS:
    def __init__(self,keys):
        self.keys=keys
        self.index=0

    def get_key(self):
        if self.index==len(self.keys):
            return ""
        return self.keys[self.index]

    def quota_exhausted(self):
        if self.index<len(self.keys):
            self.index+=1 # updating the index

    def last_used_key(self):
        if self.index==0:
            return ""
        return self.keys[self.index-1]

api_key_object=API_KEYS(API_KEYS_LIST)

def youtube_search(maxResults=50):
    if len(API_KEYS_LIST)==0:
        print("Provide API KEYS")
        return
    try:
        key=api_key_object.get_key()
        if key=="":
            print("Reached end of list of API KEYS.")
            raise Exception
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=key)
        latest_video=Video.objects.order_by("-publishing_datetime").first() # Getting lastest stored video (latest video = Video with have been published most recently out of all the stored videos)
        if latest_video is not None:
            last_publishing_datetime=latest_video.publishing_datetime.isoformat() # Getting datetime of lastest stored video
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
        api_key_object.quota_exhausted() # If quota exhausted then update the index
        error_message=f"Quota Exhausted on API key = {api_key_object.last_used_key()}"
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
    a = ThreadJob(youtube_search,event,10) # calling youtube_search function async after every 10 sec
    a.start()
    return render(request,"backend/index.html")

def get_data(request):
    page=1
    order="publishing_datetime"
    maxResults=10
    publishedAfter=None
    if 'page' in request.GET:
        page=request.GET.get('page')
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
    page_obj=paginator.get_page(page)
    videos=page_obj.object_list
    serializer=Video_Serializer(videos,many = True)
    return JsonResponse({"videos":serializer.data,"num_pages":paginator.num_pages})


