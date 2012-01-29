import cgi

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
    is_first_name_first = models.BooleanField(default=True)    
    
    def get_fullname(self):
        fullname = ''
        
        if self.is_first_name_first:
            fullname += self.owner.first_name + self.owner.last_name
        else:
            fullname += self.owner.lastname + self.owner.first_name
            
        if '' == fullname:
            fullname = self.owner.username
        
        return fullname
    
    fullname = get_fullname
    
@receiver(post_save, sender=User, 
          dispatch_uid='hypo.models.create_user_profile')
def _create_user_profile(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        profile = UserProfile(user=instance)
        profile.save()    


class UserForm(forms.ModelForm):
    ''''''
    fullname = forms.CharField()
    is_first_name_first = forms.BooleanField(initial=True)
    
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined')


class Post(models.Model):
    '''A Hypo post'''    
    source = models.TextField()
    output = models.TextField()
    summary = models.CharField(max_length=140, blank=True, default='')
    
    id_str = models.CharField(max_length=255, default='')
    author = models.ForeignKey(User)
    
    F_PLAIN = 0
    F_HTML = 1
    F_MARKDOWN = 2
    FORMATS = {
        F_PLAIN: F_PLAIN, 
        F_HTML: F_HTML, 
        F_MARKDOWN: F_MARKDOWN
    }
    format = models.PositiveSmallIntegerField(choices=FORMATS.items(), 
                                              default=F_PLAIN)    
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