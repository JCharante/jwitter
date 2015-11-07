function downvote() {
    $(document).on('click','#downvote',function(event){
        tweet_id = $(event.target).next().text();
        $.get( "http://localhost:8000/downvote/" +  tweet_id, function( data ) {
            event.target.innerHTML = data;
        });
    });
}


function upvote() {
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


function main () {
    $(".tweet_input_field").focus();
    downvote();
    upvote();
    log_out_button();
}

$(document).ready(main);