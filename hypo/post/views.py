# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
                        HttpResponseForbidden
from django.contrib.auth.models import User

import hypo.models as hypo

class StreamV(gv.ListView):
    ''''''
    model = hypo.Post
    template_name = 'hypo/pg/post_list.html'
    context_object_name = 'post_list'
    
    def get_queryset(self):
        site = hypo.Site.from_request(self.request)        
        if not site:
            raise Http404()
        
        queryset = hypo.Post.objects.filter(site=site).order_by('-updated')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(StreamV, self).get_context_data(**kwargs)
        context['site'] = hypo.Site.from_request(self.request)
        context['owner'] = context['site'].owner
        
        return context
    
    
class CreateV(gv.CreateView):
    model = hypo.Post
    template_name = 'hypo/pg/post_form.html'
    form_class = hypo.PostForm
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        user = self.request.user
        site = hypo.Site.from_request_or_user(self.request)
        
        if not user.get_profile().has_perm(site, 'post'):
            return HttpResponseForbidden()
        
        post = hypo.Post(owner=user, site=site, 
                         text_source=form.cleaned_data['text_source'],
                         title=form.cleaned_data['title'])
        post.save()
        
        self.object = post # hack for super methods to work
        return HttpResponseRedirect(self.success_url)


class DetailV(gv.DetailView):
    model = hypo.Post
    template_name = 'hypo/pg/post_detail.html'
    
    def get_object(self):
        site = hypo.Site.from_request(self.request)
        try:
            post = hypo.Post.objects.get(id_str=self.kwargs['id_str'], 
                                         site=site)
        except hypo.Post.DoesNotExist:
            raise Http404()
        else:
            return post


class UpdateV(gv.UpdateView):
    model = hypo.Post
    template_name = 'hypo/pg/post_form.html'
    form_class = hypo.PostForm

    def get_object(self):
        try:
            post = hypo.Post.objects.get(id_str=self.kwargs['id_str'])
            
            if not self.request.user.get_profile().has_perm(post, 'update'):
                return HttpResponseForbidden()
            
        except hypo.Post.DoesNotExist:
            raise Http404()
        else:
            return post
        
        
class DeleteV(gv.DeleteView):
    model = hypo.Post
    success_url = '/dashboard/'
    template_name = 'hypo/pg/post_detail.html'
    
    def get_object(self):
        try:
            post = hypo.Post.objects.get(id_str=self.kwargs['id_str'])
            
            if not self.request.user.get_profile().has_perm(post, 'delete'):
                return HttpResponseForbidden()
            
        except hypo.Post.DoesNotExist:
            raise Http404()
        else:
            return post
        
    def get_context_data(self, **kwargs):
        context = super(DeleteV, self).get_context_data(**kwargs)
        context['confirm_delete'] = True
        
        return context