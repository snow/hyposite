from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',
    #url(r'^$', login_required(v.MenuV.as_view())),
    url(r'^importxml/$', login_required(v.ImportXMLV.as_view())),
)
