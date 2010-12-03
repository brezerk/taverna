
$(document).ready(function(){
    $(".vote-positive").click(function(event){
        vote_async($(this).attr('id'), 1);
        event.preventDefault();
    });
    $(".vote-negative").click(function(event){
        vote_async($(this).attr('id'), 0);
        event.preventDefault();
    });
});

function vote_async(post_id, positive){
    if (!post_id)
        return;

    post_id = post_id.substring(9);

    $.getJSON('/lib/ajax.so.' + post_id + '.' + positive, {}, function(json){
        if (json.vote.message){
            var vote_msg = "#message-" + post_id;
            $(vote_msg).html("<span class='vote-negative'><a href='/man/errors/'>" + json.vote.message + "</a></span>");
        } else {
            var vote_id = "#rating-" + post_id;
            $(vote_id).html(json.vote.rating);            
        };
    }, 'json');
};

