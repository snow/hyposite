from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',
    url(r'^$', v.StreamV.as_view()),
    #url(r'^album/(?P<id>\d+)/$', v.AlbumV.as_view()),
    #url(r'^tag/(?P<tagname>.+)/$', v.TagV.as_view()),
                       
    #url(r'^upload/', login_required(v.UploadFormV.as_view())),                   
    #url(r'^upload.(?P<format>json|html)$', login_required(v.UploadFormV.as_view())),
    
    url(r'^upload_raw/$', login_required(v.UploadRawV.as_view())),
    #url(r'^gruburi.(?P<format>json|html)', ''),
    
    #url(r'^delete/$', login_required(v.BatchDeleteV.as_view())),
)
