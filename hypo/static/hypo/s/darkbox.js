/**
 * darkbox
 * --------------------
 */
(function($){
    hypo.darkbox = {};
    var clsr = hypo.darkbox;
    
    clsr.thumb_list_uri = null;
    
    clsr.E_SHOW_IMG = 'evt-hypo-darkbox-show_img';
    
    var j_darkbox,
        j_hd,
        j_bd,
        j_main,
        j_main_img,
        j_sidebar,
        j_ft,
        
        initialized = false,
        is_shown = false,
        
        PLACEHOLDER_URI = '/s/common/i/loading-31.gif';
    
    function init(){
        if(initialized){return;}
        
        j_darkbox = $($('#darkbox_tpl').text()).appendTo($('body'));
        j_hd = j_darkbox.find('header');
        j_bd = j_darkbox.find('.bd');
        j_main = j_darkbox.find('.col_m')
        j_main_img = j_darkbox.find('img');
        j_sidebar = j_darkbox.find('.col_r');
        j_ft = j_darkbox.find('footer');
        j_thumb_list = j_ft.find('.thumb_list');
        
        rcp.preimg(PLACEHOLDER_URI);
        rcp.preimg('/s/common/i/view-40.png');
        rcp.preimg('/s/common/i/arrow-l-45_93.png');
        rcp.preimg('/s/common/i/arrow-r-45_93.png');
        
        initialized = true;
        
        $(window).on('resize', function(evt){
            is_shown && layout()
        });
        
        j_darkbox.on(clsr.E_SHOW_IMG, load_thumbs);
    }
        
    function init_check(){
        if(true !== initialized){
            throw 'darkbox did not successful init.';
        }
    }
        
    function layout(){
        init_check();
        
        var darkbox_height = j_darkbox.height(),
            header_height = j_hd.height(),
            footer_height = j_ft.height(),
            body_height = darkbox_height - header_height - footer_height,
            body_width = j_darkbox.width(),
            sidebar_width = j_sidebar.width(),
            main_col_width = body_width - sidebar_width;
        
        j_main.height(body_height);
        j_main.width(main_col_width);
    }
    
    function extract_from_dom(j_t){
        init_check();
        
        return {
            j_img: j_t.find('img'),
            j_hd: j_t.find('.darkbox_header'),
            j_sidebar: j_t.find('.darkbox_sidebar')
        };
    }
    
    function pre_show(){
        j_main_img.attr('src', PLACEHOLDER_URI);
    }
    
    function show(target){
        j_main_img.attr('src', target.j_img.attr('src')).
                   attr('alt', target.j_img.attr('alt'));
                   
        j_hd.empty().append(target.j_hd);
        j_sidebar.empty().append(target.j_sidebar);
        
        j_darkbox.trigger(clsr.E_SHOW_IMG, [target]);
    }
    
    function on(){
        init_check();
        j_darkbox.show();
        layout();
        is_shown = true;
    }
    
    function off(){
        init_check();
        j_darkbox.hide();
        is_shown = false;
    }
    
    clsr.from_dom = function(j_target){
        initialized || init();
        
        var target = extract_from_dom(j_target.remove());
        on();
        pre_show();
        show(target);
    };
    
    clsr.from_uri = function(uri){
        initialized || init();
        
        on();
        pre_show();
        $('<div />').load('{} #darkbox2init'.replace('{}', uri), function(evt){
            var target = extract_from_dom($(this)); 
            show(target);
        });
    }
    
    function load_thumbs(evt, target){
        if(!clsr.thumb_list_uri){return;}
        
        var num_prev_to_load = 5,
            num_next_to_load = 15,
            imgid = target.j_img.attr('imgid'),
            since = imgid,
            till = imgid,
            j_cur_thumb = j_ft.find('[imgid={}]'.replace('{}', imgid)),
            j_prev = j_cur_thumb.prevAll('[imgid]'),
            j_next = j_cur_thumb.nextAll('[imgid]'),
            
            adjust_cur_after_load = false;
            
        if(0 === j_cur_thumb.length){
            since = parseInt(imgid) - 1;
            adjust_cur_after_load = true;
        }
        
        if(j_prev.length){
            num_prev_to_load = num_prev_to_load - j_prev.length;
            since = j_prev.shift().attr('imgid');
        }
        
        if(num_prev_to_load){
            prepend_thumbs(since, num_prev_to_load, adjust_cur_after_load);
        }
        
        if(j_next.length){
            num_next_to_load = num_next_to_load - j_next.length;
            till = j_next.pop().attr('imgid');
        }
        
        if(num_next_to_load > 10){
            append_thumbs(till, num_next_to_load);
        }
    }
    
    function prepend_thumbs(since, count, adjust_cur_after_load){
        var uri = '{u}?since={s}&count={c}'.replace('{u}', clsr.thumb_list_uri).
                                            replace('{c}', count).
                                            replace('{s}', since);
        $('<div />').load(uri, function(evt){
            var j_ls = $(this).find('.thumb_container');
            
            for(var i=j_ls.length-1; 0<=i; i--){
                var j_t = $(j_ls.get(i)),
                    imgid = j_t.attr('imgid'),
                    j_exist = j_thumb_list.find('[imgid={}]'.replace('{}', 
                                                                     imgid));
                    
                if(0 === j_exist.length){
                    j_thumb_list.prepend(j_t);
                    
                    if(adjust_cur_after_load){
                        j_t.addClass('on');
                    }
                }
                
                adjust_cur_after_load = false;
            }
        });
    }
    
    function append_thumbs(till, count){
        var uri = '{u}?till={t}&count={c}'.replace('{u}', clsr.thumb_list_uri).
                                            replace('{c}', count).
                                            replace('{t}', till);
        $('<div />').load(uri, function(evt){
            var j_ls = $(this).find('.thumb_container');
            
            for(var i=0; i<j_ls.length; i++){
                var j_t = $(j_ls[i]),
                    imgid = j_t.attr('imgid'),
                    j_exist = j_thumb_list.find('[imgid={}]'.replace('{}', 
                                                                     imgid));
                    
                if(0 === j_exist.length){
                    j_thumb_list.append(j_t);
                }
            }
        });
    }
})(jQuery);