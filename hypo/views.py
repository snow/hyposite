# Create your views here.
import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

import hypo.models as hypo

class UnderConstructionV(gv.TemplateView):
    template_name = 'hypo/pg/under_construction.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['back_to'] = request.META.get('HTTP_REFERER', '/')
        
        return super(UnderConstructionV, self).get(request, *args, **kwargs)
    
class IndexV(gv.TemplateView):
    template_name = 'hypo/pg/index.html'
    
#    def get_context_data(self, *args, **kwargs):
#        context = super(IndexV, self).get_context_data(*args, **kwargs)
#        context['querystring'] = self.request.GET.urlencode()
#        return context
#    
#    def get(self, request, *args, **kwargs):
#        if request.user.is_authenticated():
#            return HttpResponseRedirect('/dashboard/')
#        else:                
#            self.queryset = ikr.ImageCopy.objects.order_by('-id')[0:50]
#            return super(IndexV, self).get(request, *args, **kwargs)    
