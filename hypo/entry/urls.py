from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',
    url(r'^$', v.StreamV.as_view()),
    #url(r'^tags/(?P<tagname>.+)/$', v.TagV.as_view()),
)
