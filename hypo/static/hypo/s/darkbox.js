/**
 * darkbox
 * --------------------
 */
(function($){
    hypo.darkbox = {};
    var clsr = hypo.darkbox;
    
    var j_darkbox,
        j_hd,
        j_bd,
        j_main,
        j_main_img,
        j_prev,
        j_next,
        j_sidebar,
        j_ft,
        
        j_surveymeter = $('<div id="darkbox-pgcenter-surveymeter" '+
            'style="position:fixed; top:50%; left:50%; width:0; height:0;" />'),
        
        initialized = false,
        is_shown = false,
        
        E_SHOW_IMG = 'evt-hypo-darkbox-show_img',
        E_NEXT = 'evt-hypo-darkbox-next',
        E_PREV = 'evt-hypo-darkbox-prev',
        
        PLACEHOLDER_URI = '/s/common/i/loading-31.gif';
        
    function init_evt(){        
        j_darkbox.on('click', '.next', function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            j_darkbox.trigger(E_NEXT);
        }).
        on('click', '.prev', function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            j_darkbox.trigger(E_PREV);
        }).
        on('click', '.x', function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            hide_darkbox();
        }).
        on('click', function(evt){
            if(j_hd.is(':visible')){
                j_hd.hide();
                j_sidebar.hide();
                j_ft.hide();
                layout();
            } else {
                j_hd.show();
                j_sidebar.show();
                j_ft.show();
                layout();
            }
        }).
        on(E_SHOW_IMG, set_current_thumb).
        on(E_THUMBS_ADDED, adjust_thumb_list_width).
        on(E_NEXT, on_next).
        on(E_PREV, on_prev);
        
        j_thumb_list.on('click', '.thumb_container', function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            clsr.from_uri($(this).attr('href'));
        });
        
        //rcp.debug() && rcp.l('[darkbox] init event');
    }
    
    function init_keyboard(){
        rcp.j_doc.on('keydown', function(evt){
            if(is_shown){
                switch(evt.which){
                case 27: // esc
                    hide_darkbox();
                    break;
                    
                case 37: // left
                case 72: // h
                case 65: //a
                    j_darkbox.trigger(E_PREV);
                    break;
                    
                case 39: // right
                case 76: // l
                case 68: //d
                    j_darkbox.trigger(E_NEXT);
                    break;
                }
            }
        });
        
        //rcp.debug() && rcp.l('[darkbox] init keyboard');
    }
    
    function init(){
        if(initialized){return;}
        
        j_darkbox = $($('#darkbox_tpl').text()).appendTo($('body'));
        j_hd = j_darkbox.find('header');
        j_bd = j_darkbox.find('.bd');
        j_main = j_darkbox.find('.col_m')
        j_main_img = j_darkbox.find('img');
        j_prev = j_darkbox.find('.prev');
        j_next = j_darkbox.find('.next');
        j_sidebar = j_darkbox.find('.col_r');
        j_ft = j_darkbox.find('footer');
        j_thumb_list = j_ft.find('.thumb_list');
        
        rcp.preimg(PLACEHOLDER_URI);
        rcp.preimg('/s/common/i/view-40.png');
        rcp.preimg('/s/common/i/arrow-l-45_93.png');
        rcp.preimg('/s/common/i/arrow-r-45_93.png');
        
        init_evt();
        init_keyboard();
        
        $(window).on('resize', function(evt){
            is_shown && layout()
        });
        
        initialized = true;
    }
        
    function init_check(func_name){
        if(true !== initialized){
            throw '{}: darkbox did not successful init.'.replace('{}', 
                                                                 func_name);
        }
    }
        
    function layout(){
        init_check('layout');
        
        var darkbox_height = j_darkbox.height(),
            header_height = j_hd.is(':visible')?j_hd.height():0,
            footer_height = j_ft.is(':visible')?j_ft.height():0,
            body_height = darkbox_height - header_height - footer_height,
            body_width = j_darkbox.width(),
            sidebar_width = j_sidebar.is(':visible')?j_sidebar.width():0,
            main_col_width = body_width - sidebar_width,
            arrow_width = parseInt(main_col_width / 4);
        
        j_main.height(body_height);
        j_main.width(main_col_width);
        j_prev.width(arrow_width);
        j_next.width(arrow_width);
        j_next.css('left', main_col_width-arrow_width);
    }
    
    function extract_from_dom(j_t){
        init_check('extract_from_dom');
        
        return {
            j_img: j_t.find('img'),
            j_hd: j_t.find('.darkbox_header'),
            j_sidebar: j_t.find('.darkbox_sidebar')
        };
    }
    
    function pre_show(){
        j_main_img.attr('src', PLACEHOLDER_URI);
    }
    
    function show_image(target){
        j_main_img.attr('src', target.j_img.attr('src')).
                   attr('alt', target.j_img.attr('alt'));
                   
        j_hd.empty().append(target.j_hd);
        j_sidebar.empty().append(target.j_sidebar);
        
        j_darkbox.trigger(E_SHOW_IMG, [target]);
    }
    
    function show_darkbox(){
        init_check('on');
        j_darkbox.show();
        layout();
        is_shown = true;
    }
    
    function hide_darkbox(){
        init_check('off');
        j_darkbox.hide();
        is_shown = false;
    }
    
    clsr.from_dom = function(j_target){
        initialized || init();
        
        var target = extract_from_dom(j_target.remove());
        show_darkbox();
        pre_show();
        show_image(target);
    };
    
    clsr.from_uri = function(uri){
        initialized || init();
        
        show_darkbox();
        pre_show();
        $('<div />').load('{} #darkbox2init'.replace('{}', uri), function(evt){
            var target = extract_from_dom($(this)); 
            show_image(target);
        });
    };
    
    //
    // optional thumb list functions
    //    
    var _thumb_width = false,
    
        E_THUMBS_ADDED = 'evt-hypo-darkbox-thumbs_added';
    
    clsr.append_thumb_from_uri = function(uri){
        initialized || init();
        
        uri = uri.replace('/images/', '/images/thumbs/');
        
        $('<div />').load(uri, function(evt){
            j_thumb_list.append($(this).find('.thumb_container'));
            j_darkbox.trigger(E_THUMBS_ADDED);
        });
    };
    
    function get_thumb_width(){
        init_check('get_thumb_width');
        
        if(!_thumb_width){
            var j_thumb = j_thumb_list.find('.thumb_container:first'),
                j_img = j_thumb.find('img');
            
            // j_thumb.width() may not be right as image may not be loaded
            _thumb_width = parseInt(j_thumb.outerWidth()) + 
                           parseInt(j_img.outerWidth());
        }              
        
        return _thumb_width;
    }
    
    function adjust_thumb_list_width(evt){
        init_check('adjust_thumb_list_width');
        
        j_thumb_list.width(get_thumb_width() * 
                           j_thumb_list.find('.thumb_container').length + 10);
    }
    
    function set_current_thumb(evt, target){
        init_check('set_current_thumb');
        
        var imgid = target.j_img.attr('imgid'),
            j_cur_thumb = j_ft.find('[imgid={}]'.replace('{}', imgid));
        
        j_thumb_list.find('.thumb_container.on').removeClass('on');
        j_cur_thumb.addClass('on');
        center_current_thumb(j_cur_thumb);
    }
    
    function center_current_thumb(j_thumb){
        init_check('center_current_thumb');
        
        if(!j_thumb){
            j_thumb = j_thumb_list.find('.on');
        }
        
        if(!j_thumb.length){return;}
        
        j_surveymeter.appendTo($('body'));
        var offset = j_surveymeter.offset();
        j_surveymeter.detach();
        
        thumb_target_left = offset.left - j_thumb.outerWidth() / 2;
        thumb_cur_left = j_thumb.offset().left;
        list_cur_left = j_thumb_list.offset().left;
        j_thumb_list.css(
            'left', list_cur_left + (thumb_target_left - thumb_cur_left)
        );
    }
    
    function on_prev(evt){
        init_check('on_prev');
        var j_t = j_thumb_list.find('.on').prev();
        if(j_t.length){
            clsr.from_uri(j_t.attr('href'));
        }
    }
    
    function on_next(evt){
        init_check('on_next');
        var j_t = j_thumb_list.find('.on').next();
        if(j_t.length){
            clsr.from_uri(j_t.attr('href'));
        }
    }
})(jQuery);