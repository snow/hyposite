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


class DashboardV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/dashboard.html'
                                 
    def get(self, request, *args, **kwargs):
        '''dev only'''
        #site = hypo.Site.objects.get(owner=request.user)
        return HttpResponseRedirect(request.user.get_profile().primary_site.uri)
                                 
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
            initial['slug'] = self.request.session['username'].replace('.', '_')
            
        if 'fullname' in self.request.session:
            initial['fullname'] = self.request.session['fullname']
            initial['title'] = '{}\'s Blog'.format(initial['fullname'])
            
        return initial            
    
    def form_valid(self, form):
        if 'account_to_link' not in self.request.session:
            raise Exception('missing account to link')
        else:
            account_to_link = self.request.session['account_to_link']
        
        # use email as username
        user = User.objects.create_user(form.cleaned_data['email'], 
                                        form.cleaned_data['email'])
        
        self.object = user # hack for super methods to work
        
        profile = user.get_profile()        
        profile.fullname = form.cleaned_data['fullname']
        profile.timezone = form.cleaned_data['timezone']
        profile.save()
        
        account_to_link.owner = user
        account_to_link.save()
        
        site = hypo.Site(owner=user, slug=form.cleaned_data['slug'], 
                         title=form.cleaned_data['title'])
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
        
        
class SigninV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/signin.html'
        
        
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
        
#class PostCreateV(gv.CreateView):
#    ''''''
#    form_class = hypo.ArticleForm
#    template_name = 'hypo/pg/post_create.html'
#    success_url = '/dashboard/'
#    
#    def form_valid(self, form):
#        post = hypo.Post(author=self.request.user, 
#                         title=form.cleaned_data['title'])
#        post.modify_content(form.cleaned_data['content_source'], 
#                            form.cleaned_data['format'])
#        post.save()
#        
#        self.object = post # hack for super methods to work
#        return HttpResponseRedirect(self.success_url)
#    
#    
#class SiteV(gv.DetailView):
#    ''''''
#    model = hypo.Site
#    template_name = 'hypo/pg/post_list.html'
#    
#    def get_context_data(self, **kwargs):
#        context = super(SiteV, self).get_context_data(**kwargs)
#        context['owner'] = self.object.owner
#        context['post_list'] = hypo.Post.objects.filter(author=self.object)
#        
#        return context
    
    
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
        return self.request.user.get_profile().primary_site
    

#class PhotoStreamV(gv.DetailView):
#    ''''''
#    model = User
#    slug_field = 'username'
#    context_object_name = 'owner'
#    template_name = 'hypo/pg/photo_list.html'
#    
#    def get_context_data(self, **kwargs):
#        context = super(PhotoStreamV, self).get_context_data(**kwargs)
#        context['site'] = hypo.Site.objects.get(owner=self.object)
#        #context['photo_list'] = hypo.Post.objects.filter(author=self.object)
#        
#        return context
     
#class LuciferV(gv.View):
#    '''Evil codes'''
#    def get(self, request, *args, **kwargs):
#        fucker = '''<h1>fucker</h1>
#<p style="font-size:xx-large">this is just a <br />
#paragraph</p>
#<p>Lorem Ipsum is<br /> 
#simply <br />
#dummy text of the <br />
#printing <br />
#and<br /> 
#typesetting <br />
#industry. Lorem<br /> 
#Ipsum has<br /> 
#been the industry's standard dummy <br />
#text ever since the 1500s, when an <br />
#unknown printer took a galley of type and <br />
#scrambled it to make a type specimen book. <br />
#It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</p>
#<div>what the fuck</div>
#    
#<script>alert('im evil!');</script>'''
#        
#        output, summary = hypo.Post.process_html_content_source(fucker) 
#        
#        return HttpResponse('<pre>{}</pre>'.format(summary))