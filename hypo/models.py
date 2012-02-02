import cgi
import hashlib

from BeautifulSoup import BeautifulSoup 
from pyrcp import struk
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django import forms

# Create your models here.
class UserProfile(models.Model):
    '''
    User profile
    
    only use for storing extra data of an user 
    other models associate with user by django.contrib.auth.models.User
    '''
    user = models.ForeignKey(User, unique=True)
    fullname = models.CharField(max_length=255)
    about = models.TextField()
    avatar_uri = models.URLField()
    
    def save(self, *args, **kwargs):
        if '' == self.fullname:
            self.fullname = self.user.username
            
        return super(UserProfile, self).save(*args, **kwargs)
    
    def get_gravatar_uri(self):
        return 'http://www.gravatar.com/avatar/{}?s=120&d=monsterid'.\
            format(hashlib.md5(self.user.email.strip().lower()).hexdigest())
    
@receiver(post_save, sender=User, 
          dispatch_uid='hypo.models.create_user_profile')
def _create_user_profile(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        profile = UserProfile(user=instance)
        profile.save()


class Site(models.Model):
    ''''''
    owner = models.ForeignKey(User, unique=True)
    title = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        if '' == self.title:
            self.title = '{}\'s Blog'.format(self.owner.get_profile().fullname)
            
        return super(Site, self).save(*args, **kwargs)


class UserForm(forms.ModelForm):
    ''''''
    email = forms.EmailField()
    
    class Meta:
        model = UserProfile
        fields = ('fullname', 'about')
        
    def save(self, *args, **kwargs):
        profile = super(UserForm, self).save(*args, **kwargs)
        if profile:
            user = profile.user
            user.email = self.cleaned_data['email']
            user.save()
            
        return profile
        
        
class SiteForm(forms.ModelForm):
    ''''''
    username = forms.CharField(max_length=30)
    
    class Meta:
        model = Site
        exclude = ('owner',)
        
    def save(self, *args, **kwargs):
        site = super(SiteForm, self).save(*args, **kwargs)
        if site:
            user = site.owner
            user.username = self.cleaned_data['username']
            user.save()
            
        return site
        
        
class SignupForm(forms.ModelForm):
    ''''''
    fullname = forms.CharField(max_length=255)
    title = forms.CharField(max_length=255)
    
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined')                
        
        
class Post(models.Model):
    '''A Hypo post'''    
    title = models.CharField(max_length=30, blank=True, default='')
    
    content_source = models.TextField()
    content_summary = models.CharField(max_length=140, blank=True, default='')
    content = models.TextField()
    F_PLAIN = 0
    F_HTML = 1
    F_MARKDOWN = 2
    FORMATS = {
        F_PLAIN: 'plain',
        F_HTML: 'html',
        F_MARKDOWN: 'markdown',
    }
    format = models.PositiveSmallIntegerField(choices=FORMATS.items(), 
                                              default=F_PLAIN)
    #link = models.URLField()
    
#    T_STATUS = 0
#    T_ARTICLE = 1
#    T_LINK = 2
#    T_IMAGE = 3
#    TYPES = {
#        T_STATUS: T_STATUS,
#        T_ARTICLE: T_ARTICLE,
#        T_LINK: T_LINK,
#        T_IMAGE: T_IMAGE,
#    }
#    type = models.PositiveSmallIntegerField(choices=TYPES.items(), 
#                                            default=T_STATUS)
    id_str = models.CharField(max_length=255, default='')
    author = models.ForeignKey(User)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def modify_content(self, source, format):
        self.content_source = source
        self.format = format
        
        if self.F_PLAIN == self.format:
            self.content, self.content_summary = \
                self.process_plain_content_source(source)
        elif self.F_HTML == self.format:
            self.content, self.content_summary = \
                self.process_html_content_source(source)
        else:
            raise NotImplemented()
        
    def get_content_format(self):
        return self.FORMATS[self.format]
        
    @classmethod
    def process_plain_content_source(cls, source):
        content = cgi.escape(source)
        summary = cls.extract_content_summary(content)
        
        return (content, summary)

    _ALLOWED_HTML_ATTRS = ['id', 'title', 'dir', 'lang', 'xml:lang', 'href', 
                           'rel', 'src', 'alt']
    @classmethod
    def process_html_content_source(cls, source):   
        soup = BeautifulSoup(source)
        
        for tag in soup.findAll():
            if 'script' == tag.name:
                tag.extract()
            else:
                for attr in tag.attrs:
                    if attr[0] not in cls._ALLOWED_HTML_ATTRS:
                        del tag[attr[0]]
        
        summary = cls.extract_content_summary(''.join(soup.findAll(text=True)))
        
        content = soup.prettify()
        return (content, summary)
    
    @classmethod
    def extract_content_summary(cls, content):
        summary = str(content)
        
        if 137 < len(summary):
            return '{}...'.format('\n'.join(summary[:137].split('\n')[:10]))
        else:
            return ''
    
@receiver(post_save, sender=Post, 
          dispatch_uid='hypo.models.assign_post_id_str')
def _assign_post_id_str(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        instance.id_str = struk.int2str(instance.id)
        instance.save()
        
        
class PostForm(forms.ModelForm):
    ''''''
    class Meta:
        model = Post
        fields = ('title', 'content_source', 'format')