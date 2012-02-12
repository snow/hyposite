# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import django.views.generic as gv
from django.conf import settings

#import flickrapi

#from pyfyd.models import TwitterAccount, GoogleAccount, DoubanAccount, \
#                         FlickrAccount
#import pyfyd.google.views as pgv
#import pyfyd.twitter.views as ptv
#
#import pyfyd.flickr.views as pfv
#from core.models import GrubJob
#from core.grub.grubbers.flickr import PeopleStreamGrubber

#class IndexV(gv.TemplateView):
#    template_name = 'hypo/thirdparty.html'
#    
#    def get_context_data(self, *args, **kwargs):
#        context = super(IndexV, self).get_context_data(*args, **kwargs)
#        
#        try:
#            context['douban_account'] = DoubanAccount.objects.\
#                                            get(owner=self.request.user)
#        except DoubanAccount.DoesNotExist:
#            context['douban_account'] = False
#            
#        try:
#            context['google_account'] = GoogleAccount.objects.\
#                                            get(owner=self.request.user)
#        except GoogleAccount.DoesNotExist:
#            context['google_account'] = False
#            
#        try:
#            context['twitter_account'] = TwitterAccount.objects.\
#                                            get(owner=self.request.user)
#        except TwitterAccount.DoesNotExist:
#            context['twitter_account'] = False
#            
#        try:
#            context['flickr_account'] = FlickrAccount.objects.\
#                                            get(owner=self.request.user)
#        except FlickrAccount.DoesNotExist:
#            context['flickr_account'] = False
#            
#        return context
#import pyfyd.douban.views as pdv
#import pyfyd


class ImportMenuV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/import_menu.html'


#
#class DoubanAuthenticateStartV(pdv.AuthStartV):
#    '''super handles every thing'''    
#    callback = '/thirdparty/douban/authenticate_return/'
#    
#class DoubanAuthenticateReturnV(pdv.AuthenticateReturnV):
#    '''super handles every thing'''
#    success_uri = '/dashboard/'
    
#class DoubanAuthorizeStartV(pdv.AuthStartV):
#    '''super handles every thing'''    
#    callback = '/thirdparty/douban/authorize_return/'
#    
#class DoubanAuthorizeReturnV(pdv.AuthorizeReturnV):
#    '''super handles every thing'''
#    success_uri = '/thirdparty/'
#    
#    def get(self, request, *args, **kwargs):
#        super(DoubanAuthorizeReturnV, self).get(request, *args, **kwargs)
#        
#        return HttpResponseRedirect(self.success_uri)    
    
    
#class GoogleAuthenticateStartV(pgv.AuthStartV):
#    '''super handles every thing'''
#    callback = '/thirdparty/google/authenticate_return/'
#    
#class GoogleAuthenticateReturnV(pgv.AuthenticateReturnV):
#    '''super handles every thing'''
#    success_uri = '/dashboard/'
#    
#class GoogleAuthorizeStartV(pgv.AuthStartV):
#    '''super handles every thing'''
#    callback = '/thirdparty/google/authorize_return/'
#    
#class GoogleAuthorizeReturnV(pgv.AuthorizeReturnV):
#    '''super handles every thing'''
#    success_uri = '/thirdparty/'    
#    
#    def get(self, request, *args, **kwargs):
#        super(GoogleAuthorizeReturnV, self).get(request, *args, **kwargs)
#        
#        return HttpResponseRedirect(self.success_uri)    
    
    
#class TwitterAuthenticateStartV(ptv.AuthStartV):
#    '''super handles every thing'''    
#    callback = '/thirdparty/twitter/authenticate_return/'
#    signin = True
#    
#class TwitterAuthenticateReturnV(ptv.AuthenticateReturnV):
#    '''super handles every thing'''
#    success_uri = '/dashboard/'
#    
#class TwitterAuthorizeStartV(ptv.AuthStartV):
#    '''super handles every thing'''    
#    callback = '/thirdparty/twitter/authorize_return/'
#    signin = False
#    
#class TwitterAuthorizeReturnV(ptv.AuthorizeReturnV):
#    '''super handles every thing'''
#    success_uri = '/thirdparty/'    
#    
#    def get(self, request, *args, **kwargs):
#        super(TwitterAuthorizeReturnV, self).get(request, *args, **kwargs)
#        
#        return HttpResponseRedirect(self.success_uri)    
    
#class FlickrAuthorizeStartV(pfv.AuthStartV):
#    '''super handles every thing'''    
#    #callback = '/thirdparty/flickr/authorize_return/'
#    
#class FlickrAuthorizeReturnV(pfv.AuthorizeReturnV):
#    '''super handles every thing'''
#    success_uri = '/thirdparty/'    
#    
#    def get(self, request, *args, **kwargs):
#        super(FlickrAuthorizeReturnV, self).get(request, *args, **kwargs)
#        
#        return HttpResponseRedirect(self.success_uri)
#    
#class FlickrImportV(gv.View):
#    ''''''
#    
#    def post(self, request):
#        ''''''
#        try:
#            flickr_account = FlickrAccount.objects.get(owner=request.user)
#        except FlickrAccount.DoesNotExist:
#            raise Exception('no flickr account linked')
#        else:
#            job = GrubJob(type=PeopleStreamGrubber.TYPE, user=request.user, 
#                          priority=GrubJob.HIGH_PRIORITY)
#            job.save()
#            
#        return HttpResponse('done')