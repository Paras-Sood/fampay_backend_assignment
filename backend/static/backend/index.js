var page_no=1,publishedAfter="",maxResults=10,order="publishing_datetime";
document.addEventListener('DOMContentLoaded',()=>{
    console.log("Here")
    load_videos()
    document.querySelector('#filters').onsubmit = function(){
        publishedAfter=document.querySelector('#publishedAfter').value
        maxResults=document.querySelector('#maxResults').value
        order=document.querySelector('#order').value
        page_no=1;
        load_videos()
        return false
    }
})
function load_videos(){
    let url;
    if(publishedAfter===""){
        url=`/get_data?page=${page_no}&maxResults=${maxResults}&order=${order}`
    }else{
        url=`/get_data?page=${page_no}&maxResults=${maxResults}&order=${order}&publishedAfter=${publishedAfter}`
    }
    fetch(url)
        .then(response=>response.json())
        .then(response=>{
            document.querySelector('#videos_div').innerHTML="";
            console.log(response)
            if(response.error){
                document.querySelector('#videos_div').innerHTML=`<h2>${response.error}</h2>`;
            }else{
                response.videos.forEach(video => {
                    add_video(video,"videos_div")
                });
                pagination(response.num_pages,page_no)
            }
        })
}
function add_video(video,location_id){
    let video_div=document.createElement('div')
    video_div.className="list-item"
    video_div.style.display='flex'
    video_div.style.flexDirection='column'
    let title=document.createElement('h3')
    title.innerHTML=`<strong>Title - </strong>${video.title}`
    let description=document.createElement('p')
    description.innerHTML=`<strong>Description - </strong>${video.description}`
    let datetime=document.createElement('span')
    datetime.innerHTML=`<strong>Published on </strong>${new Date(video.publishing_datetime)}`
    let thumbnail_div=document.createElement('div')
    thumbnail_div.innerHTML="<strong>Thumbnail Urls - </strong>"
    for(let i=0;i<video.thumbnails.length;i++){
        let thumbnail=document.createElement('p')
        thumbnail.innerHTML=video.thumbnails[i].link;
        thumbnail_div.append(thumbnail)
    }
    video_div.append(title)
    video_div.append(description)
    video_div.append(datetime)
    video_div.append(thumbnail_div)
    document.querySelector(`#${location_id}`).append(video_div)
}
function pagination(num_pages,current_page){
    const ul=document.querySelector('#paginationul');
    ul.innerHTML='';
    let previous=document.createElement('li')
    let a=document.createElement('a')
    let disabled="disabled";
    if(current_page>1){
        disabled=""
    }
    previous.className=`page-item ${disabled}`
    a.className='page-link'
    a.innerHTML='Previous'
    a.addEventListener('click',()=>{
        page_no-=1;
        load_videos();
    });
    previous.append(a);
    ul.append(previous);
    let i=current_page,last=current_page;
    if(current_page>1) i-=1;
    if(current_page<num_pages) last+=1;
    let active="";
    for(;i<=last;i++){
        if(i===current_page)    active="active";
        else    active="";
        let page=document.createElement('li')
        page.className=`page-item ${active}`
        let span=document.createElement('span')
        span.className="page-link"
        span.innerHTML=i
        span.addEventListener('click',function(){
            page_no=parseInt(this.innerHTML);
            load_videos();
        })
        page.append(span);
        ul.append(page);
    }
    let next=document.createElement('li')
    disabled="disabled"
    if(current_page<num_pages){
        disabled=""
    }
    next.className=`page-item ${disabled}`
    let an=document.createElement('a')
    an.className='page-link'
    an.innerHTML='Next'
    an.addEventListener('click',()=>{
        page_no+=1;
        load_videos();
    });
    next.append(an);
    ul.append(next);
}