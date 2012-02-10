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
    
    def get_queryset(self):
        site = hypo.Site.from_request(self.request)        
        if not site:
            raise Http404()
        
        queryset = hypo.ImageCopy.objects.filter(site=site).order_by('-created')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(StreamV, self).get_context_data(**kwargs)
        context['site'] = hypo.Site.from_request(self.request)
        context['owner'] = context['site'].owner
        context['page_title'] = 'Recent Images'
        
        return context


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

        