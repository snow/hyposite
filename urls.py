from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('hypo.urls')),
    
    # @todo: dynamic next_page
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/'}),
    url(r'^accounts/signout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/'}),                   
    # Examples:
    # url(r'^$', 'prjhypo.views.home', name='home'),
    # url(r'^prjhypo/', include('prjhypo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

_nemo_root = getattr(settings, 'NEMO_URI_ROOT', False)
if _nemo_root:    
    urlpatterns += patterns('',
        url(_nemo_root[1:], include('nemo.urls')),
    )
