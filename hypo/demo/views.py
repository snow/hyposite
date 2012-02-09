import django.views.generic as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

class FeedV(gv.TemplateView):
    ''''''
    template_name = 'hypo/demo/feed.html'
    
class StatusListV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'
    
class ArticleListV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'
    
class ImageListV(gv.TemplateView):
    ''''''
    template_name = 'hypo/demo/images.html'
    
class ArchiveV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'
    
class TagV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'
    
class AboutV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'
    
class ArticleV(gv.TemplateView):
    ''''''
    template_name = 'hypo/pg/under_construction.html'