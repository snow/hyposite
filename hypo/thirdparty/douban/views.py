# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import django.views.generic as gv
from django.conf import settings
#from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import authenticate, login

from pyfyd.models import DoubanAccount
from pyfyd.utils import ThirdpartyAuthBackend
import pyfyd.douban.views as pdv


class AuthenticateStartV(pdv.AuthStartV):
    '''super handles every thing'''    
    callback = '/thirdparty/douban/authenticate_return/'
    
    
class AuthenticateReturnV(pdv.AuthReturnV):
    '''super handles every thing'''
    success_uri = '/dashboard/'
    
    def get(self, request):
         # get self.access_token and self.uid available
        super(AuthenticateReturnV, self).get(request)
        
        account = DoubanAccount.get_from_token(self.access_token.key, 
                                               self.access_token.secret, 
                                               self.uid)
        try:
            linked = DoubanAccount.get_linked(account)
        except DoubanAccount.DoesNotExist:
            request.session.update({
                'account_to_link': account,
                'username': account.username,
                'fullname': account.fullname,
            })
            
            return HttpResponseRedirect('/accounts/signup/')
        else:
            user = authenticate(account=linked, CID=ThirdpartyAuthBackend.CID)
            
            if user:
                login(request, user)
                return HttpResponseRedirect(self.success_uri)
            else:
                # @todo: what else may happen here?
                raise Exception('auth failed')
        
    
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
#    
#    