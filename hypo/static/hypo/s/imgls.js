/**
 * image list
 * --------------------
 */
(function($){
    ikr.imgls = {
        E_IMG_REMOVED: 'evt-ikr-img_removed',
        E_IMG_LOADED: 'evt-ikr-img_loaded',
        
        E_LOADMORE: 'evt-ikr-loadmore',
        
        E_SELECTION_CHANGE: 'evt-ikr-selection_change',
        
        owner_name: false,
        album_id: false
    };
    
    var j_imgctn_tpl, 
        j_meta_tpl,
        j_actionbar, 
        j_selected_count,
        
        initialized = false,
        
        selected = [],
        is_selection_locked = false,
        
        API_DEL_URI = '/api/img/delete/',
        API_PUBLIC_STREAM_URI = '/api/img/list/public/till{till}.html/',
        API_PEOPLE_STREAM_URI = '/api/img/list/people/{username}/till{till}.html/',
        API_ALBUM_STREAM_URI = '/api/album/list/{album_id}/till{till}.html/',
        API_MOVE2ALBUM_URI = '/api/img/move_to_album/{album_id}/';
        
    ikr.imgls.init = function(){
        if(initialized){return;}
        
        j_actionbar = $('.actionbar.batch');
        j_selected_count = j_actionbar.find('.stat .count');
        
        j_imgctn_tpl = ikr.j_imgls.find('.imgctn.tpl').remove().removeClass('tpl');
        j_meta_tpl = j_imgctn_tpl.find('.meta.tpl').remove().removeClass('tpl');
        //rcp.l(ikr.j_imgls);
        //rcp.l(ikr.j_imgls.find('.imgctn.tpl'));
        
        ikr.j_imgls.on('click', '.wrap', function(evt){
            if(is_selection_locked){return;}
            
            $(evt.target).closest('.imgctn').toggleClass('on');
            ikr.j_imgls.trigger(ikr.imgls.E_SELECTION_CHANGE);
        }).
        on(ikr.imgls.E_SELECTION_CHANGE, function(evt){
            var j_selected = ikr.j_imgls.find('.imgctn.on'),
                selected_count = j_selected.length;
            
            j_selected_count.text(selected_count);
            
            selected = [];
            
            if(selected_count>0){
                j_actionbar.show();
                
                $.each(j_selected, function(idx, el){
                    selected.push($(el).attr('imgid'));
                });
            } else {
                j_actionbar.hide();
            }
        }).
        on(ikr.imgls.E_LOADMORE, loadmore_handler);
        
        rcp.j_doc.on('scroll', function(evt){
            var dis_to_btm = rcp.j_doc.height() - rcp.j_doc.scrollTop() - 
                             window.innerHeight;
                             
            if(400 > dis_to_btm){
                //loadmore();
                ikr.j_imgls.trigger(ikr.imgls.E_LOADMORE);
            }
        });
        
        j_actionbar.on('click', '.select .clear', function(evt){
            evt.preventDefault();
            if(is_selection_locked){return;}
            
            ikr.j_imgls.find('.imgctn').removeClass('on');
            ikr.j_imgls.trigger(ikr.imgls.E_SELECTION_CHANGE);
        }).
        on('click', '.select .all', function(evt){
            evt.preventDefault();
            if(is_selection_locked){return;}
            
            ikr.j_imgls.find('.imgctn').addClass('on');
            ikr.j_imgls.trigger(ikr.imgls.E_SELECTION_CHANGE);
        }).
        on('click', '.select .inverse', function(evt){
            evt.preventDefault();
            if(is_selection_locked){return;}
            
            ikr.j_imgls.find('.imgctn').toggleClass('on');
            ikr.j_imgls.trigger(ikr.imgls.E_SELECTION_CHANGE);
        }).
        on('click', '.move2album .ext a', function(evt){
            evt.preventDefault();
            is_selection_locked = true;
            
            var album_id = /^\/album\/(\d+)\//.exec($(this).attr('href'))[1],
                j_2move = ikr.j_imgls.find('.imgctn.on'),
                ids = [];
            
            $.each(j_2move, function(idx, el){
                var j_t = $(el);
                
                j_t.addClass('ing').find('.status').text('moving');
                    
                ids.push(j_t.attr('imgid'));
            });
            
            $.ajax(API_MOVE2ALBUM_URI.replace('{album_id}', album_id), {
                type: 'POST',
                data: {'ids':ids.join(',')},
                success: function(data){
                    ;
                },
                error: function(xhr, textStatus, errorThrown){
                    j_2move.removeClass('ing').addClass('err');
                    j_2move.find('.status').text('error');
                },
                complete: function(){
                    is_selection_locked = false;
                }
            });
        }).
        on('click', '.del', function(evt){
            evt.preventDefault();
            is_selection_locked = true;
            
            var j_2del = ikr.j_imgls.find('.imgctn.on'),
                ids = [];
            
            $.each(j_2del, function(idx, el){
                var j_t = $(el);
                
                j_t.addClass('ing').find('.status').text('deleting');
                    
                ids.push(j_t.attr('imgid'));
            });
            
            $.ajax(API_DEL_URI, {
                type: 'POST',
                data: {'ids':ids.join(',')},
                success: function(data){
                    j_2del.fadeOut(function(){
                        j_2del.remove();
                        ikr.j_imgls.trigger(ikr.imgls.E_SELECTION_CHANGE);
                    });
                    
                    ikr.j_imgls.trigger(ikr.imgls.E_IMG_REMOVED, [j_2del]);
                },
                error: function(xhr, textStatus, errorThrown){
                    j_2del.removeClass('ing').addClass('err');
                    j_2del.find('.status').text('error');                    
                },
                complete: function(){
                    is_selection_locked = false;
                }
            });
        });
        
        initialized = true;
        /*rcp.l(function(){
            var count = 0;
            
            j_imgctn_tpl.length && (count++);
            j_meta_tpl.length && (count++);
            
            return '[imgls] init done {}/2'.replace('{}', count);
        });*/
    }
    
    function loadmore_handler(evt){
        if(ikr.j_imgls.hasClass('ing')){return;}
        
        ikr.j_imgls.addClass('ing');
        
        var j_lastimg = ikr.j_imgls.find('.imgctn:last'),
            api = false;
            
        if(ikr.imgls.album_id){
            api = API_ALBUM_STREAM_URI.replace('{album_id}', 
                                               ikr.imgls.album_id);
        } else if(ikr.imgls.owner_name) {
            api = API_PEOPLE_STREAM_URI.replace('{username}', 
                                                ikr.imgls.owner_name);
        } else {
            api = API_PUBLIC_STREAM_URI;
        }
        
        api = api.replace('{till}', j_lastimg.attr('imgid'));
        
        $('<div />').load(api, function(){
            var j_tmp = $(this),
                j_imgs = j_tmp.find('.imgctn');
                
            if(j_imgs.length){
                $.each(j_imgs, function(idx, el){
                    var j_t = $(el);
                    j_t.appendTo(ikr.j_imgls);
                    ikr.j_imgls.trigger(ikr.imgls.E_IMG_LOADED, [j_t]);
                });
            } else {
                ikr.j_imgls.off(ikr.imgls.E_LOADMORE, loadmore_handler);
            }
            
            ikr.j_imgls.removeClass('ing');
        });
    }
    
    ikr.imgls.add_img = function(src, status, meta, append){
        var j_imgctn = j_imgctn_tpl.clone().addClass(status);
            
        j_imgctn.find('img').attr('src', src);
        j_imgctn.find('.status').text(status);
        
        if('object' === typeof meta){
            var caption = j_imgctn.find('figcaption');
            $.each(meta, function(key, value){
                var j_meta = caption.find('.'+key);
                
                if(0===j_meta.length){
                    j_meta = j_meta_tpl.clone().addClass(key).appendTo(caption);
                }
                
                if('size' === key){
                    j_meta.attr('extract', value);
                    j_meta.text(ikr.byte2mb(value) + 'mb');
                } else {
                    j_meta.text(value);
                }
            });
        }
        
        if(true === append){
            j_imgctn.appendTo(ikr.j_imgls);
        } else {
            j_imgctn.prependTo(ikr.j_imgls);
        }
    };
})(jQuery);