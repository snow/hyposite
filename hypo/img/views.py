# Create your views here.
import tempfile
import json

import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
                        HttpResponseForbidden
from django.core.files import File
from django.contrib.auth.models import User

import hypo.models as hypo

class StreamV(gv.ListView):
    ''''''
    model = hypo.ImageCopy
    template_name = 'hypo/pg/image_list.html'
    context_object_name = 'image_list'
    paginate_by = 20
    
    def get_queryset(self):
        site = hypo.Site.from_request(self.request)        
        if not site:
            raise Http404()
        
        qs = hypo.ImageCopy.objects.filter(site=site).order_by('-created')
        
        since = self.request.GET.get('since', None)
        if since:
            qs = qs.filter(pk__gt=since)
        
        till = self.request.GET.get('till', None)  
        if till:
            qs = qs.filter(pk__lt=till)
        
#        count = self.request.GET.get('count', None)
#        if not count:
#            count = 20
#        qs = qs[0:count]
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(StreamV, self).get_context_data(**kwargs)
        context['site'] = hypo.Site.from_request(self.request)
        context['owner'] = context['site'].owner
        context['page_title'] = 'Recent Images'
        context['from'] = 'stream'
        
        return context
    
    
class ThumbStreamV(StreamV):    
    template_name = 'hypo/pg/thumb_list.html'


class UploadRawV(gv.View):
    '''
    accept image uploaded as raw post data
    
    response in json
    '''
    def post(self, request):
        site = hypo.Site.from_request_or_user(self.request)
        
        if not request.user.get_profile().has_perm(site, 'image'):
            return HttpResponseForbidden()
        
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(request.raw_post_data)
        tmp.flush()
        img = hypo.ImageCopy.from_file(File(tmp), request.user, site,
                                       request.GET.get('filename', ''))
        tmp.close()
        
        return HttpResponse(json.dumps(img.dict),
                            content_type='application/json')

        
class DetailV(gv.DetailView):
    model = hypo.ImageCopy
    template_name = 'hypo/pg/image_detail.html'
    context_object_name = 'image'
    
    def get_object(self):
        site = hypo.Site.from_request(self.request)
        try:
            img = hypo.ImageCopy.objects.get(id_str=self.kwargs['id_str'], 
                                             site=site)
        except hypo.ImageCopy.DoesNotExist:
            raise Http404()
        else:
            return img     
        
    def get_context_data(self, **kwargs):
        context = super(DetailV, self).get_context_data(**kwargs)
        
        if 'from' in self.kwargs:
            site = hypo.Site.from_request(self.request)
            
            if 'stream' == self.kwargs['from']:
                context['thumbs'] = hypo.ImageCopy.objects.\
                                        filter(id__gt=self.object.id-10, 
                                               id__lt=self.object.id+10,
                                               site=site).\
                                        order_by('-created')[:20]
        
        return context   