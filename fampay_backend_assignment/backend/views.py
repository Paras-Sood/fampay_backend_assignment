from django.shortcuts import render
from googleapiclient.discovery import build

DEVELOPER_KEY = 'AIzaSyCm86IhxgixQeIucWY10SDf85eA4NCbw8M'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(
        q="cricket",
        part='id,snippet',
        maxResults=1
    ).execute()
    print(search_response)

def index(request):
    youtube_search()
    return render(request,"backend/index.html")

def main():
    pass

if __name__=="main":
    main()