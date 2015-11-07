function GetValue(element) {
     var get_text= $(element).next().find('#id').text();
     alert(get_text);
}


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

function main () {
    $(".tweet_input_field").focus();
    downvote();
    upvote();
}

$(document).ready(main);