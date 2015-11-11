function downvote() {
    $(document).on('click','#downvote',function(event){
        tweet_id = $(event.target).next().text();
        $.get( "http://localhost:8000/downvote/" +  tweet_id, function( data ) {
            event.target.innerHTML = data;
        });
    });
}

function retweet() {
    $(document).on('click','#retweet',function(event) {
        tweet_id = $(event.target).parent().prev().children('#id').text();
        $.get( "http://localhost:8000/retweet/" + tweet_id, function( data) {
            $(event.target).text(data);
        });
    });
}


function follow() {
    $(document).on('click', '#follow', function(event) {
        tweet_id = $(event.target).parent().next().children('#id').text();
        $.get( "http://localhost:8000/follow/" + tweet_id, function(data) {
            $(event.target).text(data);
        });
    });
}


function delete_tweet() {
    $(document).on('click','#delete',function(event) {
        tweet_id = $(event.target).parent().prev().children("#id").text();
        $.get( "http://localhost:8000/delete/" + tweet_id, function( data) {
            function close1() {
              $('.notification').slideUp('fast');
            }
            $(event.target).text("Tweet Deleted!");
            $('.notification').text('Tweet Deleted!');
            $('.notification').slideDown('fast');
            $(event.target).parent().parent().parent().fadeOut("slow", function() {
                $(event.target).parent().parent().parent().remove();
            });
            window.setTimeout(close1,3000);
        });
    })
}


function like() {
    $(document).on('click','#like',function(event){
        tweet_id = $(event.target).next().next().text();
        $.get( "http://localhost:8000/like/" +  tweet_id, function( data ) {
            event.target.innerHTML = data;
        });
    });
}

function log_out_button() {
    $(document).on('click','#log_out_button',function(){
        deleteCookies();
        $(location).attr('href', 'http://localhost:8000')
    });
}


function deleteCookies() {
    // Credits goes to http://stackoverflow.com/a/10593045/5006133 for this function
    function createCookie(name,value,days) {
        if (days) {
            var date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        document.cookie = name+"="+value+expires+"; path=/";
    }
    function eraseCookie(name) {
        createCookie(name,"",-1);
    }
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++)
      eraseCookie(cookies[i].split("=")[0]);
}


function youtube_video () {
    $(document).on('click','.youtube-link',function(event) {
        var video_link = $(event.target).prev().text();
        var modified_video_link = video_link.replace("youtu.be/", "youtube.com/embed/");
        bootbox.dialog({
            title: "Watch Video",
            message: '<iframe width="560" height="315" src="' + modified_video_link + '" frameborder="0" allowfullscreen></iframe>'
        });
    })
}

function picture_link () {
    $(document).on('click','.picture-link',function(event) {
        var picture_link = $(event.target).prev().text();
        bootbox.dialog({
            title: "View Image",
            message: '<img width="550px" height="auto" src="' + picture_link + '"></img>'
        });
    })
}

function main () {
    $(".tweet_input_field").focus();
    downvote();
    like();
    log_out_button();
    delete_tweet();
    retweet();
    follow();
    youtube_video();
    picture_link();
}

$(document).ready(main);