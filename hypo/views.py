# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

import hypo.models as hypo

class UnderConstructionV(gv.TemplateView):
    template_name = 'hypo/pg/under_construction.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['back_to'] = request.META.get('HTTP_REFERER', '/')
        
        return super(UnderConstructionV, self).get(request, *args, **kwargs)
    
    
class IndexV(gv.TemplateView):
    template_name = 'hypo/pg/index.html'


class SignupV(gv.CreateView):
    ''''''
    form_class = hypo.UserForm
    template_name = 'hypo/pg/signup.html'
    success_url = '/dashboard/'
    
    def get_initial(self):
        initial = {}
        
        if 'username' in self.request.session:
            initial['username'] = self.request.session['username']
            
        if 'fullname' in self.request.session:
            initial['fullname'] = self.request.session['fullname']
            
        return initial
            
    
    def form_valid(self, form):
        if 'account_to_link' not in self.request.session:
            raise Exception('missing account to link')
        else:
            account_to_link = self.request.session['account_to_link']
        
        user = User.objects.create_user(form.cleaned_data['username'], 
                                               form.cleaned_data['email'])
        
        self.object = user # hack for super methods to work
        
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        profile = user.get_profile()        
        if 'is_first_name_first' in self.request.POST:            
            profile.is_first_name_first = True
        else:
            profile.is_first_name_first = False
        profile.save()
        
        account_to_link.owner = user
        account_to_link.save()
        
        # need 'pyfyd.utils.ThirdpartyAuthBack' in 
        # settings.AUTHENTICATION_BACKENDS for this to work
        user = authenticate(account=account_to_link)            
        if user:
            login(self.request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            # if missing 'pyfyd.utils.ThirdpartyAuthBack' in settings,
            # this may happen
            raise Exception('auth failed')