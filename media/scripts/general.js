/*
# Copyright (C) 2010 by Alexey S. Malakhov <brezerk@gmail.com>
#                       Opium <opium@jabber.com.ua>
#
# This file is part of Taverna
#
# Taverna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taverna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Taverna.  If not, see <http://www.gnu.org/licenses/>.
*/

var old_post_id = 0

function highlightOnLoad(){
    anchor = (document.location.hash);

    if (anchor != null)
        objName = anchor.substr(6);
            if (objName != null)
                highlightMessage(objName);
    return;
}

function focusOnAnchor(anchor){
    var currentHref = window.location.href;
    window.location.href = currentHref.substr(0, currentHref.lastIndexOf("#")) + "#" + anchor;
    return;
}

function highlightMessage(post_id){
    postName = 'post_' + post_id;
    postObj = document.getElementById(postName);

    if (postObj != null){
            postObj.style.border = "1px solid #7e0f0f";
            if (old_post_id != post_id)
                unhighlightMessage();
            old_post_id = post_id;
        }
    return;
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
    return;
}


