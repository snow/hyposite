/**
 * uploading img
 */
(function($){
    hypo.imgupload = {};
    
    _settings = {
        SELECT_FILE_BTN_CLASS: 'selectfile',
        SELECT_FILE_BTN_TXT: 'Select local files',
        SELECT_FILE_BTN_TPL: '<a class="{class}" href="#">{txt}</a>',
        
        MASK_TPL: '<div class="dropzone">'+
                '<div class="bg"></div>'+
                '<div class="inr">drop files here</div>'+
            '</div>',
            
        ALBUM_ID: 0,
        
        get_xhr: false
    };
    
    hypo.imgupload.config = function(settings){
        $.extend(_settings, settings);
    };
    
    hypo.imgupload.enhanceform = function(field, options){
        options = $.extend({
            'auto_submit': true,
            'hide_submit': true,
            'btntpl': _settings.SELECT_FILE_BTN_TPL,
        }, options);
        
        // get reference to the field
        var j_field;
        if(field && 'string' === typeof field){
            j_field = $(field);
        } else if('object' === typeof field) {
            j_field = field;
        }
        
        // hide field and put trigger anchor
        var tpl;
        if(options.btntpl && 'string' === typeof options.btntpl){
            tpl = options.btntpl;
            tpl = tpl.replace('{class}', _settings.SELECT_FILE_BTN_CLASS);
            tpl = tpl.replace('{txt}', _settings.SELECT_FILE_BTN_TXT);
        } else {
            throw 'invalid template';
        }
        
        // this class make file filed poistion:absolute and opacity:0
        // to overlap select link
        // doesnt user like to trigger click event on file filed
        // as this may not work due to browser security policy
        j_field.wrap('<div class="imgfieldwrap" />');
        j_link = $(tpl).insertAfter(j_field);
        
        // auto submit
        if(options.auto_submit){
            var j_form = j_field.closest('form');
            j_field.on('change', function(evt){
                queue_images(evt.target.files, evt.timeStamp);
                return false;
            });
            
            if(options.hide_submit){
                j_form.find('[type=submit]').hide();
            }
        }
    };
    
    var is_drag_evt_handled = false,
    
        j_mask,
        j_inr,
        
        API_UPLOAD_URI = '/img/uploadraw/'+
                         '?filename={filename}&album_id={album_id}',
        MAX_UPLOAD_CONN = 2,
        
        cur_upload_conn = 0,
        //files_to_upload = {},
        upload_queue = [];
        
    hypo.imgupload.E_QUEUE_ADDED = 'evt-hypo-queue_added';
    hypo.imgupload.E_QUEUE_START = 'evt-hypo-queue_start';
    hypo.imgupload.E_UPLOAD_START = 'evt-hypo-upload_start';
    hypo.imgupload.E_UPLOAD_DONE = 'evt-hypo-upload_done';
    hypo.imgupload.E_UPLOAD_FAILED = 'evt-hypo-upload_failed';
    hypo.imgupload.E_UPLOAD_COMPLETE = 'evt-hypo-upload_complete';
        
    rcp.preimg('/s/common/i/loading-16.gif');
    rcp.preimg('/s/common/i/alert-16.png');
    
    hypo.imgupload.init_dnd = function(){
        j_mask = $(_settings.MASK_TPL);
        j_inr = j_mask.find('.inr');
        
        rcp.j_doc.on({
            'dragover': on_drag_over,
            'drop': on_drop,
            'keydown': function(evt){
                (27 === evt.which) && after_drop();
            }
        });
        
        rcp.j_doc.on('click', 'body>.dropzone', after_drop);
        rcp.j_doc.on(hypo.imgupload.E_QUEUE_START, on_queue_start);
        rcp.j_doc.on(hypo.imgupload.E_UPLOAD_COMPLETE, on_queue_start);
        rcp.j_doc.on(hypo.imgupload.E_UPLOAD_START, upload_file);
    }
    
    function on_drag_over(evt){
        if(!is_drag_evt_handled){
            is_drag_evt_handled = true;     
            
            evt.originalEvent.dataTransfer.dropEffect = 'copy';
            
            $('body').append(j_mask);
            j_inr.width(j_mask.width() - 
                         (j_inr.outerWidth() - j_inr.width()));
            j_inr.height(j_mask.height() - 
                          (j_inr.outerHeight() - j_inr.height()));   
        }
        return false;
    }
    
    function on_drop(evt){
        evt.preventDefault();
        queue_images(evt.originalEvent.dataTransfer.files, evt.timeStamp);
        
        after_drop();
        return false;
    }
    
    function after_drop(){
        j_mask.detach();
        is_drag_evt_handled = false;
    }
    
    function queue_images(filelist, timestamp){
        $.each(filelist, function(idx, file){
            if(/^image.(jpeg|png|gif)/.test(file.type)){
                var reader = new FileReader(),
                    id = timestamp + '-' + idx;
                    
                reader.onload = function(evt){
                    var job = {
                        'id': id,
                        'file': file,
                        'data_url': evt.target.result
                    }
                    upload_queue.push(job);
                    rcp.j_doc.trigger(hypo.imgupload.E_QUEUE_ADDED, [job]);
                    rcp.j_doc.trigger(hypo.imgupload.E_QUEUE_START);
                }
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    function on_queue_start(evt){
        while(upload_queue.length && cur_upload_conn < MAX_UPLOAD_CONN){
            rcp.j_doc.trigger(hypo.imgupload.E_UPLOAD_START, 
                              [upload_queue.shift()]);
        }
    }
    
    function upload_file(evt, job){
        var id = job.id,
            file = job.file,
            filename = file.name,
            ajax_settings = {
                type: 'POST',
                data: file,
                processData: false,
                dataType: 'json',
                contentType: 'application/octet-stream',
                success: function(resp, textStatus, jqXHR){
                    //rcp.l(resp);
                    rcp.j_doc.trigger(hypo.imgupload.E_UPLOAD_DONE, [resp]);
                },
                error: function(xhr, textStatus, errorThrown){
                    rcp.j_doc.trigger(hypo.imgupload.E_UPLOAD_FAILED, [xhr]);
                },
                complete: function(){
                    cur_upload_conn -= 1;
                    rcp.j_doc.trigger(hypo.imgupload.E_UPLOAD_COMPLETE);
                }
            },
            url = API_UPLOAD_URI.replace('{filename}', filename).
                                 replace('{album_id}', _settings.ALBUM_ID);
                                 
        if($.isFunction(_settings.get_xhr)){
            ajax_settings.xhr = _settings.get_xhr; 
        }
            
        cur_upload_conn += 1;
        
        $.ajax(url, ajax_settings);
    }
})(jQuery);
