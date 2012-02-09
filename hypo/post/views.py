# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

import hypo.models as hypo

#class StreamV(gv.DetailView):
#    ''''''
#    model = User
#    slug_field = 'username'
#    context_object_name = 'owner'
#    template_name = 'hypo/pg/image_list.html'
#    
#    def get_context_data(self, **kwargs):
#        context = super(StreamV, self).get_context_data(**kwargs)
#        context['site'] = hypo.Site.objects.get(owner=self.object)
#        context['image_list'] = hypo.ImageCopy.objects.\
#                                    filter(owner=self.object).order_by('-id')
#        
#        return context
    

class CreateV(gv.CreateView):
    model = hypo.Article
    template_name = 'hypo/pg/article_form.html'
    form_class = hypo.ArticleForm
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        user = self.request.user
        site = hypo.Site.objects.get(is_primary=True, owner=user)
        
        article = hypo.Article.create(user, site, 
                                      form.cleaned_data['content_source'],
                                      title=form.cleaned_data['title'])
        
        self.object = article # hack for super methods to work
        return HttpResponseRedirect(self.success_url)


        