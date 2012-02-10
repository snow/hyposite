from hypo.models import Site

class SitePerms(object):
    '''TODO'''
    def __init__(self, request):
        self.user = request.user
        self.site = Site.from_request(request)
        if self.user.is_authenticated():
            self.user_profile = self.user.get_profile()
        else:
            self.user_profile = None
        
    def __getitem__(self, key):
        if self.user_profile:
            if 'site_settings' == key:
                return self.user == self.site.owner
            else:
                return self.user_profile.has_perm(self.site, key)
        else:
            return False

def site_perms(request):
    return dict(site_perms=SitePerms(request))