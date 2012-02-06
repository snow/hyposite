/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	config.uiColor = '#fff';
	
	config.toolbar_basic = [
	   ['Bold', 'Italic', 'Strike', 'Subscript', 'Superscript', '-', 
	    'NumberedList', 'BulletedList', '-',
	    'Blockquote', '-',
	    'Image', 'Link', 'Unlink','-',
	    'RemoveFormat', '-',
	    'Source']
	];
	config.toolbar = 'basic';
	config.toolbarCanCollapse = false;
	
	config.removePlugins = 'about, elementspath, flash';
	
	config.resize_dir = 'vertical';
	
	config.extraPlugins = 'autogrow';	
	config.autoGrow_onStartup = true;
	config.autoGrow_maxHeight = 400;
	config.autoGrow_minHeight = 200;
	config.autoGrow_bottomSpace = 30;
};

CKEDITOR.on('instanceReady', function( evt ) {
    var block_tags = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 
                      'li', 'blockquote', 'ul', 'ol', 'table', 'thead', 'tbody',
                      'tfoot', 'td', 'th'];

    for (var i=0; i < block_tags.length; i++)
    {
        evt.editor.dataProcessor.writer.setRules(block_tags[i], {
            indent: false,
            breakBeforeOpen: true,
            breakAfterOpen: false,
            breakBeforeClose: false,
            breakAfterClose: true
        });
    }
});
