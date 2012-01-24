from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v 

urlpatterns = patterns('',
    url(r'^$', v.UnderConstructionV.as_view()),
    #url(r'^$', v.IndexV.as_view()),
    #url(r'^dashboard/$', login_required(v.DashboardV.as_view())),
    
    url(r'^under_construction/$', v.UnderConstructionV.as_view()),
)
