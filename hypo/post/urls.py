from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',
    url(r'^$', v.StreamV.as_view()),
    url(r'^tagged/(?P<tag_name>[^/]+)/$', v.StreamV.as_view()),
    
    url(r'^c/$', login_required(v.CreateV.as_view())),
    url(r'^create/$', login_required(v.CreateV.as_view())),
    
    url(r'^v/(?P<id_str>\w+)/', v.DetailV.as_view()),
    #url(r'^view/(?P<id_str>\w+)/', v.DetailV.as_view()),
    #url(r'^r/(?P<id_str>\w+)/', v.DetailV.as_view()),
    #url(r'^read/(?P<id_str>\w+)/', v.DetailV.as_view()),
    
    url(r'^u/(?P<id_str>\w+)/', v.UpdateV.as_view()),
    #url(r'^update/(?P<id_str>\w+)/', v.UpdateV.as_view()),
    
    url(r'^d/(?P<id_str>\w+)/', v.DeleteV.as_view()),
    #url(r'^delete/(?P<id_str>\w+)/', v.DeleteV.as_view()),
)
