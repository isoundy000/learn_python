/**
* EasyDrag 1.3 - Drag & Drop jQuery Plug-in
*
* For usage instructions please visit http://fromvega.com
*
* Copyright (c) 2007 fromvega
*/

(function($){

    // to track if the mouse button is pressed
    var isMouseDown    = false;

    // to track the current element being dragged
    var currentElement = null;

    // callback holders
    var dropCallbacks = {};
    var dragCallbacks = {};

    // global position records
    var lastMouseX;
    var lastMouseY;
    var lastElemTop;
    var lastElemLeft;

    // returns the mouse (cursor) current position
    $.getMousePosition = function(e){
        var posx = 0;
        var posy = 0;

        if (!e) var e = window.event;

        if (e.pageX || e.pageY) {
            posx = e.pageX;
            posy = e.pageY;
        }
        else if (e.clientX || e.clientY) {
            posx = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            posy = e.clientY + document.body.scrollTop  + document.documentElement.scrollTop;
        }

        return { 'x': posx, 'y': posy };
    }

    // updates the position of the current element being dragged
    $.updatePosition = function(e) {
        var pos = $.getMousePosition(e);

        var spanX = (pos.x - lastMouseX);
        var spanY = (pos.y - lastMouseY);

        $(currentElement).css("top",  (lastElemTop + spanY));
        $(currentElement).css("left", (lastElemLeft + spanX));
    }

    // when the mouse is moved while the mouse button is pressed
    $(document).mousemove(function(e){
        if(isMouseDown){
            // update the position and call the registered function
            $.updatePosition(e);
            if(dragCallbacks[currentElement.id] != undefined){
                dragCallbacks[currentElement.id](e);
            }

            return false;
        }
    });

    // when the mouse button is released
    $(document).mouseup(function(e){
        if(isMouseDown){
            isMouseDown = false;
            if(dropCallbacks[currentElement.id] != undefined){
                dropCallbacks[currentElement.id](e);
            }
            return false;
        }
    });

    // register the function to be called while an element is being dragged
    $.fn.ondrag = function(callback){
        return this.each(function(){
            dragCallbacks[this.id] = callback;
        });
    }

    // register the function to be called when an element is dropped
    $.fn.ondrop = function(callback){
        return this.each(function(){
            dropCallbacks[this.id] = callback;
        });
    }

    // set an element as draggable - allowBubbling enables/disables event bubbling
    $.fn.easydrag = function(allowBubbling, handle_ids){

        return this.each(function(){

            // if no id is defined assign a unique one
            if(undefined == this.id) this.id = 'easydrag'+time();

            if (handle_ids) {
                // 修改鼠标光标为移动的形状
                for (var i=0; i<handle_ids.length; i++) {
                    $("#" + handle_ids[i]).css("cursor", "move");
                }
            } else {
                $(this).css("cursor", "move");
            }
            
            // when an element receives a mouse press
            $(this).mousedown(function(e){
                if (handle_ids) {
                    // 判断是否是在拖动某个 handle
                    var srcElement;
                    if (e)
                        srcElement = e.srcElement;
                    else
                        srcElement = window.event.srcElement;
                    
                    var exists = false;
                    if (srcElement.id != undefined) {
                        for (var i=0; i<handle_ids.length; i++) {
                            if (handle_ids[i] == srcElement.id) {
                                exists = true;
                                break;
                            }
                        }
                    }
                    if (!exists)
                        return false;
                }
                // set it as absolute positioned
                $(this).css("position", "absolute");

                // set z-index
                $(this).css("z-index", "10000");

                // update track variables
                isMouseDown    = true;
                currentElement = this;

                // retrieve positioning properties
                var pos    = $.getMousePosition(e);
                lastMouseX = pos.x;
                lastMouseY = pos.y;

                lastElemTop  = this.offsetTop;
                lastElemLeft = this.offsetLeft;

                $.updatePosition(e);

                return allowBubbling ? true : false;
            });
        });
    }

})(jQuery);