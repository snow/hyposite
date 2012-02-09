from django.http import Http404

import hypo.models as hypo

class SiteVMixin(object):
    ''''''
    __site = None
    def get_site_slug(self):
        if 'site_slug' in self.kwargs:        
            return self.kwargs['site_slug']
        else:
            return None
    
    def get_site(self, slug=None, request=None):
        if not self.__site:
            if not slug:
                slug = self.get_site_slug()
            
            if slug:
                try:
                    self.__site = hypo.Site.objects.get(slug=slug)
                except hypo.Site.DoesNotExist:
                    raise Http404()
            elif request and request.user.is_authenticated():
                self.__site = hypo.Site.objects.get(owner=request.user, 
                                                    is_primary=True)
        
        return self.__site