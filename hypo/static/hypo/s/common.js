/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.hypo = {};
    
    //hypo.j_imgls = false;
    
    hypo.byte2mb = function(value){
        return Math.round(value / 1024 / 1024 * 100) / 100; 
    }
})(jQuery);

/**
 * some simple links
 * --------------------
 */
rcp.j_doc.one('ready', function(){
    /*
    $('.sec-left .create_album').click(function(evt){
            evt.preventDefault();
            
            var d = new Date(),
                title = prompt('Please input album title', d.getFullYear()+'-'+
                                                           (d.getMonth()+1)+'-'+
                                                           d.getDate()+' '+
                                                           d.getHours()+':'+
                                                           d.getMinutes());
            title && $.ajax('/api/album/create/', {
                type: 'POST',
                data: {'title': title},
                dataType: 'json',
                success: function(data){
                    if(data.done){
                        location = data.go_to;
                    }
                }
            });
        });*/
    
    
    $('.curuser').find('.messages').on('click', 'a', function(evt){
        evt.preventDefault();
        
        var j_t = $(evt.target),
            href = j_t.attr('href'),
            j_messages = j_t.closest('.messages');
        
        j_t.hide('fast', function(evt){
            j_t.remove();
            
            if(0 == j_messages.find('a').length){
                j_messages.remove();
            }
        });
        
        ('#' !== href) && $.ajax(href);
    });
});