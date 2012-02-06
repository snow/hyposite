from django.http import Http404

import hypo.models as hypo

class SiteVMixin(object):
    ''''''
    __site = None
    def get_site_slug(self):
        return self.kwargs['site_slug']
    
    def get_site(self, slug=None):
        if not self.__site:
            try:
                if not slug:
                    slug = self.get_site_slug()
                self.__site = hypo.Site.objects.get(slug=slug)
            except hypo.Site.DoesNotExist:
                raise Http404()
        
        return self.__site