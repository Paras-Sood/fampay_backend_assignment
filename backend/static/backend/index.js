var page=1;
document.addEventListener('DOMContentLoaded',()=>{
    console.log("Here")
    document.querySelector('form').onsubmit = function(){
        fetch(`/get_data?q=${document.querySelector('#query').value}`)
        .then(response=>response.json())
        .then(response=>{
            console.log(response)
            response.forEach(video => {
                add_video(video,"videos_div")
            });
            // pagination(response.num_pages,((start-1)/10)+1)
        })
        return false
    }
})
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
        start-=10;
        load_following_posts();
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
            start=(parseInt(this.innerHTML)*10-9);
            load_following_posts();
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
        start+=10;
        load_following_posts();
    });
    next.append(an);
    ul.append(next);
}