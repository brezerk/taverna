var old_post_id = 0

function highlightMessage(post_id){

    postName = 'post_' + post_id;
    postObj = document.getElementById(postName);

    if (postObj != null){
            postObj.style.border = "1px solid red";
            if (old_post_id != post_id)
                unhighlightMessage();
            old_post_id = post_id;
        }
}

function unhighlightMessage(){
    if (old_post_id <= 0)
        return;

    postName = 'post_' + old_post_id;
    postObj = document.getElementById(postName);

    if (postObj != null){
        curStyle = postObj.style.border;
        
        postObj.style.border = "";
    }
}

