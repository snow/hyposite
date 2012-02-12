from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v

urlpatterns = patterns('',    
#    url(r'^$', IndexV.as_view()),

    url(r'^import/$', v.ImportMenuV.as_view()),
    
    url(r'^douban/', include('hypo.thirdparty.douban.urls')),
    url(r'^wordpress/', include('hypo.thirdparty.wordpress.urls')),
    
#    url(r'^douban/authenticate/$', DoubanAuthenticateStartV.as_view()),
#    url(r'^douban/authenticate_return/$', DoubanAuthenticateReturnV.as_view()),
#    url(r'^douban/authorize/$', DoubanAuthorizeStartV.as_view()),
#    url(r'^douban/authorize_return/$', DoubanAuthorizeReturnV.as_view()),
                       
#    url(r'^google/authenticate/$', GoogleAuthenticateStartV.as_view()),
#    url(r'^google/authenticate_return/$', GoogleAuthenticateReturnV.as_view()),
#    url(r'^google/authorize/$', GoogleAuthorizeStartV.as_view()),
#    url(r'^google/authorize_return/$', GoogleAuthorizeReturnV.as_view()),
#                       
#    url(r'^twitter/authenticate/$', TwitterAuthenticateStartV.as_view()),
#    url(r'^twitter/authenticate_return/$', TwitterAuthenticateReturnV.as_view()),
#    url(r'^twitter/authorize/$', TwitterAuthorizeStartV.as_view()),
#    url(r'^twitter/authorize_return/$', TwitterAuthorizeReturnV.as_view()),
#    
#    url(r'^flickr/authorize/$', FlickrAuthorizeStartV.as_view()),
#    url(r'^flickr/authorize_return/$', FlickrAuthorizeReturnV.as_view()),
#    url(r'^flickr/import/$', login_required(FlickrImportV.as_view())),
)