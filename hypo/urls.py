from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

import views as v 

urlpatterns = patterns('',
    url(r'^$', v.IndexV.as_view()),
    
    
    url(r'^site/demo/$', v.DemoV.as_view()),
    url(r'^site/settings/', login_required(v.SiteSettingsV.as_view())),
    url(r'^site/(?P<slug>.+)/$', v.SiteV.as_view()),
    
    url(r'^dashboard/$', login_required(v.DashboardV.as_view())),
    
    url(r'^post/create/$', login_required(v.PostCreateV.as_view())),
    url(r'^post/create\.(?P<format>html|json)$', login_required(v.PostCreateV.as_view())),
    
    url(r'^thirdparty/', include('hypo.thirdparty.urls')),
    
    url(r'^accounts/signup/', v.SignupV.as_view()),
    url(r'^accounts/settings/$', login_required(v.AccountSettingsV.as_view())),
    
    url(r'^under_construction/$', v.UnderConstructionV.as_view()),
    
    # dev
    #url(r'^lucifer/$', v.LuciferV.as_view()),
    #url(r'^m_r/$', v.M_RV.as_view()),
)
