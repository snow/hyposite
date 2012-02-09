/**
 * uploading img
 */
(function($){
    rcp.filefield = {};
    var clsr = rcp.filefield, //shortcut
    
        settings = {
            MAX_UPLOAD_CONN: 2
        };
    
    clsr.E_QUEUE_ADDED = 'evt-rcp-filefield-queue_added';
    clsr.E_QUEUE_START = 'evt-rcp-filefield-queue_start';
    clsr.E_UPLOAD_START = 'evt-rcp-filefield-upload_start';
    clsr.E_UPLOAD_DONE = 'evt-rcp-filefield-upload_done';
    clsr.E_UPLOAD_FAILED = 'evt-rcp-filefield-upload_failed';
    clsr.E_UPLOAD_COMPLETE = 'evt-rcp-filefield-upload_complete';
        
    var count_upload_conn = 0,
        upload_queue = [];
    
    // TODO: these should not be here!! 
    rcp.preimg('/s/common/i/loading-16.gif');
    rcp.preimg('/s/common/i/alert-16.png');
    
    var _initialized = false;
    function init_if_not_yet(){
        if(_initialized){return;}
        
        _initialized = true;
        rcp.j_doc.on(clsr.E_QUEUE_START, on_queue_start);
        rcp.j_doc.on(clsr.E_UPLOAD_COMPLETE, on_queue_start);
        rcp.j_doc.on(clsr.E_UPLOAD_START, upload_file);
    }    
   
    function santilize_field_ref(field){
        var j_field;
        
        if(field && 'string' === typeof field){
            j_field = $(field);
        } else if('object' === typeof field) {
            j_field = field;
        }
        
        return j_field;
    }
    
    rcp.filefield.field2link = function(field, options){
        init_if_not_yet();
        
        options = $.extend({
            link_classes: 'selectfile',
            link_text: 'Select local files',
            link_tpl: '<a class="{classes}" href="#">{txt}</a>',
            wrap_classes: 'imgfieldwrap',
            wrap_tpl: '<div class="{classes}" />'
        }, options);
        
        // get reference to the field
        var j_field = santilize_field_ref(field);
        
        // hide field and put trigger anchor
        var j_link;
        if(options.link_tpl && 'string' === typeof options.link_tpl){
            var tpl = options.link_tpl;
            tpl = tpl.replace('{classes}', options.link_classes);
            tpl = tpl.replace('{txt}', options.link_text);
            j_link = $(tpl);
        } else {
            throw 'invalid template';
        }
        
        // this class make file filed poistion:absolute and opacity:0
        // to overlap select link
        // doesnt user like to trigger click event on file filed
        // as this may not work due to browser security policy
        var wrap = options.wrap_tpl.replace('{classes}', options.wrap_classes);
        j_field.wrap(wrap);
        j_link.insertAfter(j_field);
    };
    
    rcp.filefield.ajaxify = function(field, options){
        init_if_not_yet();
        
        options = $.extend({
            upload_uri: false,
            auto_submit: true,
            hide_submit: true,
        }, options);
        
        var j_field = santilize_field_ref(field);
            j_form = j_field.closest('form'),
            accept_mime = j_field.attr('accept');
            
        if(false === options.upload_uri){
            options.upload_uri = j_form.attr('action');
        }
        
        // auto submit
        if(options.auto_submit){
            j_field.on('change', function(evt){
                evt.preventDefault();
                queue_files(evt.target.files, options.upload_uri, accept_mime,
                            evt.timeStamp);
            });
            
            if(options.hide_submit){
                j_form.find('[type=submit]').hide();
            }
        }
    };
    
    function queue_files(filelist, upload_uri, accept_mime, timestamp){
        var mime_check = false;
        if(accept_mime){
            mime_check = new RegExp('^{}'.replace('{}', accept_mime)); 
        }
        
        $.each(filelist, function(idx, file){
            if(mime_check && !mime_check.test(file.type)){return;}
            
            var reader = new FileReader(),
                id = timestamp + '-' + idx;
                
            reader.onload = function(evt){
                var job = {
                    'id': id,
                    'file': file,
                    'upload_uri': upload_uri,
                    'data_url': evt.target.result
                }
                upload_queue.push(job);
                rcp.j_doc.trigger(clsr.E_QUEUE_ADDED, [job]);
                rcp.j_doc.trigger(clsr.E_QUEUE_START);
            }
            
            reader.readAsDataURL(file);
        });
    }
    
    function on_queue_start(evt){
        while(upload_queue.length && 
                count_upload_conn < settings.MAX_UPLOAD_CONN){
            rcp.j_doc.trigger(clsr.E_UPLOAD_START, [upload_queue.shift()]);
        }
    }
    
    function upload_file(evt, job){
        var ajax_settings = {
                type: 'POST',
                data: job.file,
                processData: false,
                dataType: 'json',
                contentType: 'application/octet-stream',
                success: function(resp, textStatus, jqXHR){
                    //rcp.l(resp);
                    rcp.j_doc.trigger(clsr.E_UPLOAD_DONE, [job, resp]);
                },
                error: function(xhr, textStatus, errorThrown){
                    rcp.j_doc.trigger(clsr.E_UPLOAD_FAILED, 
                                      [job, xhr, textStatus, errorThrown]);
                },
                complete: function(){
                    count_upload_conn -= 1;
                    rcp.j_doc.trigger(clsr.E_UPLOAD_COMPLETE);
                }
            };
            
        if(job.params){
            job.upload_uri += '?'+$.param(job.params);
        }
            
        count_upload_conn += 1;
        
        $.ajax(job.upload_uri, ajax_settings);
    }
    
    
    
    
    /*
    
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
    
    */
})(jQuery);
