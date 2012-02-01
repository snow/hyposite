import cgi
import hashlib

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django import forms

from pyrcp import struk

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
    
    source = models.TextField()
    output = models.TextField()
    F_PLAIN = 0
    F_HTML = 1
    F_MARKDOWN = 2
    FORMATS = {
        F_PLAIN: F_PLAIN, 
        F_HTML: F_HTML, 
        F_MARKDOWN: F_MARKDOWN,
    }
    format = models.PositiveSmallIntegerField(choices=FORMATS.items(), 
                                              default=F_PLAIN)
    summary = models.CharField(max_length=140, blank=True, default='')
    
    link = models.URLField()
    
    T_STATUS = 0
    T_POST = 1
    T_LINK = 2
    T_IMAGE = 3
    TYPES = {
        T_STATUS: T_STATUS,
        T_POST: T_POST,
        T_LINK: T_LINK,
        T_IMAGE: T_IMAGE,
    }
    type = models.PositiveSmallIntegerField(choices=TYPES.items(), 
                                            default=T_STATUS)
    id_str = models.CharField(max_length=255, default='')
    author = models.ForeignKey(User)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def modify_content(self, source):
        self.source = source
        
        if self.F_PLAIN == self.format:
            #self.output = cgi.escape(self.source)
            self.output = self.source
        else:
            raise NotImplemented()
        
        self.summary = self.extract_summary(self.output)
        
    def determin_type(self):
        if self.title:
            pass
        
    @classmethod
    def extract_summary(cls, output):
        return output
    
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
        fields = ('source', 'format')        