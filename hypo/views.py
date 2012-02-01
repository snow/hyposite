# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from pyfyd.utils import ThirdpartyAuthBackend

import hypo.models as hypo

class UnderConstructionV(gv.TemplateView):
    template_name = 'hypo/pg/under_construction.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['back_to'] = request.META.get('HTTP_REFERER', '/')
        
        return super(UnderConstructionV, self).get(request, *args, **kwargs)
    
    
class IndexV(gv.TemplateView):
    template_name = 'hypo/pg/index.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/dashboard/')
        else:
            return super(IndexV, self).get(request, *args, **kwargs)


class DemoV(gv.TemplateView):
    template_name = 'hypo/pg/demo.html'


class DashboardV(gv.ListView):
    ''''''
    paginate_by = 10
    model = hypo.Post
    template_name = 'hypo/pg/dashboard.html'
    
    def get_queryset(self):
        return hypo.Post.objects.filter(author=self.request.user).\
                                 order_by('-updated')
                                 
#    def get(self, request, *args, **kwargs):
#        try:
#            site = hypo.Site.objects.get(owner=request.user)
#        except hypo.Site.DoesNotExist:
#            return HttpResponseRedirect('/site/create/')
#        else:
#            return super(DashboardV, self).get(request, *args, **kwargs)

class SignupV(gv.CreateView):
    ''''''
    form_class = hypo.SignupForm
    template_name = 'hypo/pg/signup.html'
    success_url = '/dashboard/'
    
    def get_initial(self):
        initial = {}
        
        if 'username' in self.request.session:
            initial['username'] = self.request.session['username']
            
        if 'fullname' in self.request.session:
            initial['fullname'] = self.request.session['fullname']
            initial['title'] = '{}\'s Blog'.format(initial['fullname'])
            
        return initial            
    
    def form_valid(self, form):
        if 'account_to_link' not in self.request.session:
            raise Exception('missing account to link')
        else:
            account_to_link = self.request.session['account_to_link']
        
        user = User.objects.create_user(form.cleaned_data['username'], 
                                        form.cleaned_data['email'])
        
        self.object = user # hack for super methods to work
        
        profile = user.get_profile()        
        profile.fullname = form.cleaned_data['fullname']
        profile.save()
        
        account_to_link.owner = user
        account_to_link.save()
        
        site = hypo.Site(owner=user, title=form.cleaned_data['title'])
        site.save()
        
        # need 'pyfyd.utils.ThirdpartyAuthBack' in 
        # settings.AUTHENTICATION_BACKENDS for this to work
        user = authenticate(account=account_to_link, 
                            CID=ThirdpartyAuthBackend.CID)            
        if user:
            login(self.request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            # if missing 'pyfyd.utils.ThirdpartyAuthBack' in settings,
            # this may happen
            raise Exception('auth failed')
        
#    def get(self, request, *args, **kwargs):
#        if request.user.is_authenticated():
#            return HttpResponseRedirect(self.success_url)
#        else:
#            return super(SignupV, self).get(request, *args, **kwargs)
        
        
#class SiteCreateV(gv.CreateView):
#    ''''''     
#    form_class = hypo.SiteForm
#    template_name = 'hypo/pg/site_create.html'
#    success_url = '/dashboard/'
#    
#    def get_initial(self):
#        return {
#            'slug': self.request.user.username,
#            'title': self.request.user.get_profile().fullname + '\'s blog'
#        }
#        
#    def get_form(self, form_class):
#        form = super(SiteCreateV, self).get_form(form_class)
#        form.instance.owner = self.request.user
#        return form
#    
#    def get(self, request, *args, **kwargs):
#        try:
#            site = hypo.Site.objects.get(owner=request.user)
#        except hypo.Site.DoesNotExist:
#            return super(SiteCreateV, self).get(request, *args, **kwargs)
#        else:
#            return HttpResponseRedirect(self.success_url)
        
class PostCreateV(gv.CreateView):
    ''''''
    form_class = hypo.PostForm
    template_name = 'hypo/pg/post_create.html'
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        post = hypo.Post(author=self.request.user,
                         format=form.cleaned_data['format'])
        post.modify_content(form.cleaned_data['source'])
        post.save()
        
        self.object = post # hack for super methods to work
        return HttpResponseRedirect(self.success_url)
    
    
class SiteV(gv.DetailView):
    ''''''
    model = User
    slug_field = 'username'
    context_object_name = 'owner'
    template_name = 'hypo/pg/post_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(SiteV, self).get_context_data(**kwargs)
        context['site'] = hypo.Site.objects.get(owner=self.object)
        
        return context
    
    
class AccountSettingsV(gv.UpdateView):
    form_class = hypo.UserForm
    template_name = 'hypo/pg/account_settings.html'
    success_url = '/dashboard/'
    
    def get_object(self):
        return self.request.user.get_profile()
    
    
class SiteSettingsV(gv.UpdateView):
    form_class = hypo.SiteForm
    template_name = 'hypo/pg/site_settings.html'
    success_url = '/dashboard/'
    
    def get_object(self):
        return hypo.Site.objects.get(owner=self.request.user)    