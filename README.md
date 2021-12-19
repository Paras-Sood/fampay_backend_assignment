# fampay_backend_assignment
- Made a server that calls youtube API(async after every 10s) for fetching the latest videos for query="football" and stores the data of vid (fields - Video title, description, publishing datetime, thumbnails URLs) in a database. 
- Created a GET API which returns the stored video data in a paginated response sorted in descending order of published datetime.
- Made a dashboard to see the video data along with filter and sorting support.

## Description
1. __Models__:
    1. __Video__: This model contains fields - 
        1. video_id (char) - stores the id of a video. This id is the one provided by Youtube API
        2. title (char) - stores the title of the video.
        3. desccription (char) - stores the description of video.
        4. publishing_datetime (datetime) - stores the datime at which the video was published
    2. __Thumbnails__:This model contains fields - 
        1. link (url) - stores the url of the thumbnail of a video.
        2. video (Foreign Key on Video) - associates to Video Model.
        
2. __views .py Functions and their URLs__:
    1. _index_ (url - '/') - This is the default route. Renders the landing page i.e. index.html.
    2. _get\_data_ (url = '/get_data?<parameters>') - GET API for fetching the video data stored in the database. Following GET parameters can be provided -
        1. start - the starting index of receiving videos. _default = 1_
        2. order - Order in which the videos should be fetched. Eg - Date,title. _default = date_
        3. maxResults - Maximum number of results expected _default = 10_
        4. publishedAfter - Only those videos will be returned which had been published after this datetime. _default = Top 50 responses would be returned_
    3. _youtube\_search_ - Calls the youtube API and stores the data in the database


### Requirements
All the requirements have been specified in ```requirements.txt``` file

### How to run
- ```cd``` to the directory where this code is present.
- Install reuirements by running ```pip install -r requirements.txt```
- Run ```python manage.py makemigrations``` to make migrations
- Run ```python manage.py migrate``` to apply migrations
- Run ```python manage.py runserver``` to run the server
- API is available at ```http://127.0.0.1:8000/get_data```
- Dashboard can be accessed at ```http://127.0.0.1:8000```
