from django.http import HttpResponse, HttpResponseRedirect
import django.views.generic as gv
from django import forms

from hypo.models import Post
from utils import XMLParser

class WordPressXMLForm(forms.Form):
    file = forms.FileField()
    
class ImportXMLV(gv.FormView):
    ''''''
    form_class = WordPressXMLForm
    template_name = 'hypo/pg/import_wordpress_xml.html'
    success_url = '/dashboard'
    
    def form_valid(self, form):
        import logging
        l = logging.getLogger('c')
        
        file = form.cleaned_data['file']
        
        if not file:
            raise Exception('no file')
        
        if 'text/xml' != file.content_type:
            raise Exception('invalid file type')
        
        user = self.request.user
        site = user.get_profile().primary_site
        
        for e_post in XMLParser.extract_posts_from_file(file):
            title = XMLParser.extract_title(e_post)
            text = XMLParser.extract_text(e_post)
            tags = XMLParser.extract_tags(e_post)
            utcdatetime = XMLParser.extract_datetime(e_post)
            
            post = Post(owner=user, site=site, title=title, text_source=text, 
                        created=utcdatetime.timestamp)
            post.save()
            post.tag_str = ','.join(tags)
            
        return HttpResponseRedirect(self.success_url)
                
            