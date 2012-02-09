# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

import hypo.models as hypo
from hypo.utils import SiteVMixin

class StreamV(gv.ListView, SiteVMixin):
    ''''''
    model = hypo.Post
    template_name = 'hypo/pg/post_list.html'
    context_object_name = 'post_list'
    
    def get_queryset(self):
        #site = self.get_site(request=self.request)
        site = self.get_site()
        owner = site.owner
        queryset = hypo.Post.objects.filter(owner=owner, site=site).\
                                     order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(StreamV, self).get_context_data(**kwargs)
        context['site'] = self.get_site()
        context['owner'] = context['site'].owner
        
        return context
    

class CreateV(gv.CreateView, SiteVMixin):
    model = hypo.Post
    template_name = 'hypo/pg/post_form.html'
    form_class = hypo.PostForm
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        user = self.request.user
        site = self.get_site(request=self.request)
        
        if not user.get_profile().could_post_on(site):
            return HttpResponseForbidden()
        
        post = hypo.Post(owner=user, site=site, 
                         text_source=form.cleaned_data['text_source'],
                         title=form.cleaned_data['title'])
        post.save()
        
        self.object = post # hack for super methods to work
        return HttpResponseRedirect(self.success_url)


        