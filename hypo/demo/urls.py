from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',
    url(r'^$', v.FeedV.as_view()),
    url(r'^statuses/$', v.StatusListV.as_view()),
    url(r'^articles/$', v.ArticleListV.as_view()),
    url(r'^images/$', v.ImageListV.as_view()),
    url(r'^archive/$', v.ArchiveV.as_view()),
    
    url(r'^tag/(?P<tagname>)/$', v.TagV.as_view()),
    
    url(r'^about/$', v.AboutV.as_view()),
    
    url(r'^articles/(?P<pk>\d+)/$', v.ArticleV.as_view()),
)
