# -*- coding: UTF-8 -*-
import cgi
import json
import hashlib
import os
from datetime import datetime
import time
import tempfile
import re
from urllib2 import quote
import math

from BeautifulSoup import BeautifulSoup 
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.db.models.fields.files import FieldFile
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.dispatch import receiver
from django import forms
from django.conf import settings
from PIL import Image
import pyexiv2 
from pyrcp import struk

from hypo.utils.utcdatetime import UTCDatetime, SimpleTZ

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
    timezone = models.SmallIntegerField(default=0)
    
    def get_gravatar_uri(self):
        return 'http://www.gravatar.com/avatar/{}?s=120&d=monsterid'.\
            format(hashlib.md5(self.user.email.strip().lower()).hexdigest())
    
    @property    
    def primary_site(self):
        return Site.objects.get(owner=self.user, is_primary=True)
    
    def has_perm(self, object, perm=''):
        if isinstance(object, Site):
            return object.owner == self.user
        elif isinstance(object, Post):
            return object.site.owner == self.user
        
        return False
    
    @property
    def post_tags(self):
        posts = self.user.post_set.all()
        tag_dict = {}
        for post in posts:
            for tag in post.tags.all():
                if tag.name in tag_dict:
                    tag_dict[tag.name].count += 1
                else:
                    tag_dict[tag.name] = tag
                    tag_dict[tag.name].count = 1
        
        tag_ls = tag_dict.values()
        return Tag.build_tag_cloud(tag_ls)
        
    
@receiver(post_save, sender=User, 
          dispatch_uid='hypo.models.create_user_profile')
def _create_user_profile(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        profile = UserProfile(user=instance, 
                              fullname=instance.username)
        profile.save()


class Site(models.Model):
    ''''''
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, unique=True)
    is_primary = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if '' == self.title:
            self.title = '{}\'s Blog'.format(self.owner.get_profile().fullname)
            
        return super(Site, self).save(*args, **kwargs)
    
    @property
    def uri(self):
        server_name = getattr(settings, 'SERVER_NAME', False)
        
        if server_name:
            return '//{}.{}/'.format(self.slug, server_name)
        else:
            return '/site/{}/'.format(self.slug)
    
    @classmethod
    def from_request(cls, request):
        slug = None
                
        server_name = getattr(settings, 'SERVER_NAME', False)        
        if server_name and request.META['HTTP_HOST'].endswith(server_name):
            l = len(server_name)
            subdomain = request.META['HTTP_HOST'][:-(l+1)]
            
            if subdomain:
                slug = subdomain
        
        else:
            matches = re.match('/site/([-\w]+)/', request.path_info)
            if matches:
                slug = matches.groups()[0]
        
        if slug:
            try:
                site = cls.objects.get(slug=slug)
                return site
            except cls.DoesNotExist:
                return None
                
        return None
            
    @classmethod
    def from_request_or_user(cls, request):
        site = cls.from_request(request)
        if site:
            return site
        elif request.user.is_authenticated():
            return request.user.get_profile().primary_site
        else:
            return None
    

class UserForm(forms.ModelForm):
    ''''''
    email = forms.EmailField()
    
    class Meta:
        model = UserProfile
        fields = ('fullname', 'about', 'timezone')
        
    def save(self, *args, **kwargs):
        profile = super(UserForm, self).save(*args, **kwargs)
        if profile:
            user = profile.user
            user.email = self.cleaned_data['email']
            user.username = self.cleaned_data['email']
            user.save()
            
        return profile
        
        
class SiteForm(forms.ModelForm):
    ''''''
    class Meta:
        model = Site
        fields = ('slug', 'title')
        
        
class SignupForm(forms.ModelForm):
    ''''''
    fullname = forms.CharField(max_length=255)
    slug = forms.SlugField(max_length=255)
    title = forms.CharField(max_length=255)
    email = forms.EmailField(required=True)
    timezone = forms.IntegerField()
    
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login', 'date_joined')


class Tag(models.Model):
    ''''''
    WEIGHT_STEP = 4
    
    name = models.CharField(max_length=255, unique=True)
    count = 0
    weight = 0
    
    @property
    def slug(self):
        return quote(self.name.encode('utf-8'), safe='')
    
    @classmethod
    def build_tag_cloud(cls, tag_ls):
        max_count = 0
        
        for tag in tag_ls:
            max_count = max(max_count, tag.count)
            
        import logging
        l = logging.getLogger('c')
        #l.debug('max_count: '+str(max_count))
        
        for tag in tag_ls:
            tag.weight = int(float(tag.count) / max_count * \
                                (cls.WEIGHT_STEP + 1))
            if tag.weight == cls.WEIGHT_STEP:
                tag.weight -= 1
            
            #l.debug('weight: '+str(tag.weight))
            
        return tag_ls
        
        
class Post(models.Model):
    '''A post may contain title, text content and images'''    
    id_str = models.CharField(max_length=255)
    slug = models.SlugField() # used in url as descript, it is NOT unique
    
    title = models.CharField(max_length=100, blank=True)
    
    text_source = models.TextField()
    text_summary = models.CharField(max_length=140, blank=True)
    text = models.TextField(blank=True)
    
    images = models.ManyToManyField('ImageCopy')
    
    tags = models.ManyToManyField(Tag)
    
    created = models.PositiveIntegerField()
    updated = models.PositiveIntegerField()
    owner = models.ForeignKey(User)
    site = models.ForeignKey(Site) 
    
    @property
    def tag_str(self):
        if self.id:
            return ', '.join([tag.name for tag in self.tags.all()])
        else:
            return ''
    
    @tag_str.setter
    def tag_str(self, str):
        tags = str.replace(u'，', u',').split(',')
        
        self.tags.clear()
        
        for tag_name in tags:
            tag_name = tag_name.strip()
            
            if tag_name:
                try:
                    tag = Tag.objects.get(name=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag(name=tag_name)
                    tag.save()
                    
                self.tags.add(tag)
    
    def get_absolute_url(self):
        return u'{}posts/v/{}/{}/'.format(self.site.uri, self.id_str, self.slug)
    
    @property
    def uri(self):
        return self.get_absolute_url()
    
    @property
    def summary(self):
        return self.text_summary
    
    @property
    def updated_datetime(self):
        dt = UTCDatetime(self.updated)
        return dt.get_local_datetime(hours=self.owner.get_profile().timezone)

    _ALLOWED_HTML_ATTRS = ['id', 'title', 'dir', 'lang', 'xml:lang', 'href', 
                           'rel', 'src', 'alt', 'target']
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
        
        plain = ''.join(soup.findAll(text=True))
        summary = cls.extract_content_summary(plain)
        
        content = soup.prettify()
        return (content, plain, summary)
    
    @classmethod
    def extract_content_summary(cls, content):
        summary = content
        
        if 137 < len(summary):
            lines = summary[:137].split('\n')[:10]
            return u'{}...'.format('\n'.join(lines))
        else:
            return ''

@receiver(pre_save, sender=Post, dispatch_uid='hypo.models.post_pre_save')
def _post_pre_save(instance, **kwargs):
    ''''''
    instance.text, content_plain, instance.text_summary = \
        Post.process_html_content_source(instance.text_source)
        
    slug = instance.title or instance.text_summary or content_plain
    #slug = slug.strip().replace(' ', '_')
    #instance.slug = quote(slug.encode('utf-8'), safe='')[:50]
    instance.slug = slug.strip().replace(' ', '_')[:50]
    
    import logging
    l = logging.getLogger('c')
    #l.debug(instance.title)
    
    if not instance.created:
        instance.created = time.mktime(datetime.utcnow().timetuple())
    
    if not instance.updated:
        instance.updated = instance.created
    
@receiver(post_save, sender=Post, 
          dispatch_uid='hypo.models.post_post_save')
def _post_post_save(instance, created, **kwargs):
    ''''''
    if not instance.id_str:
        instance.id_str = struk.int2str(instance.id)
        instance.save()
        
        
class PostForm(forms.ModelForm):
    ''''''
    tag_str = forms.CharField()
    
    class Meta:
        model = Post
        fields = ('title', 'text_source')
        
        
class ImageFile(models.Model):
    '''
    A persistenced image file under lying of a ImageCopy
    
    Could have multiple references, each owned by unique user.
    Also may have no reference. Maybe gabage collected at this situation.
    '''
    id_str = models.CharField(max_length=255, unique=True, null=True)
    md5 = models.CharField(max_length=255, unique=True)
    created = models.PositiveIntegerField()
    
    SIZE_FULL = 'f'
    SIZE_LARGE = 'l'
    SIZE_MEDIAN = 'm'
    SIZE_SMALL = 's'
    SIZE_THUMB_LARGE = 'tl'
    SIZE_THUMB_MEDIAN = 'tm'
    SIZE_THUMB_SMALL = 'ts'
    
    SIZE_LIMITS = {
        SIZE_LARGE: (2048, 2048),
        SIZE_MEDIAN: (640, 640),
        SIZE_SMALL: (200, 200),
        SIZE_THUMB_LARGE: (180, 180),
        SIZE_THUMB_MEDIAN: (120, 120),
        SIZE_THUMB_SMALL: (72, 72),
    }
    
    def gen_dirname(self):
        return datetime.now().strftime('uimg/%Y/%m/%d')
    
    def gen_filename(self, size=SIZE_FULL):
        if self.SIZE_FULL == size:
            size = ''
        else:
            size = '_' + size
        
        return '{dir}/{id_str}{size}.jpg'.format(dir=self.gen_dirname(), 
                                                 id_str=self.id_str, size=size)
        
    file = models.ImageField(upload_to=gen_filename, null=True)
    
    width_f = models.PositiveIntegerField(default=0)
    height_f = models.PositiveIntegerField(default=0)
    width_l = models.PositiveIntegerField(default=0)
    height_l = models.PositiveIntegerField(default=0)
    width_m = models.PositiveIntegerField(default=0)
    height_m = models.PositiveIntegerField(default=0)
    width_s = models.PositiveIntegerField(default=0)
    height_s = models.PositiveIntegerField(default=0)
    width_tl = models.PositiveIntegerField(default=0)
    height_tl = models.PositiveIntegerField(default=0)
    width_tm = models.PositiveIntegerField(default=0)
    height_tm = models.PositiveIntegerField(default=0)
    width_ts = models.PositiveIntegerField(default=0)
    height_ts = models.PositiveIntegerField(default=0)
        
    def get_uri(self, size=SIZE_SMALL):
        uri = self.file.url
        
        if self.SIZE_FULL == size:
            return uri
        else:
            path, ext = os.path.splitext(uri)
            return ''.join((['{}_{}'.format(path, size), ext])) 
        
    def resample(self):
        '''Generate image file of all sizes from FULL'''
        img_f = Image.open(self.file.path)
        imgpath_noext = os.path.splitext(self.file.path)[0]
        ORIGIN_WIDTH = img_f.size[0]
        ORIGIN_HEIGHT = img_f.size[1]
        
        for size in self.SIZE_LIMITS:
            # resize and crop for thumb sizes
            if 't' == size[0]:
                # resize based on the shorter edge
                if ORIGIN_WIDTH > ORIGIN_HEIGHT:
                    new_height = self.SIZE_LIMITS[size][1]
                    scale = float(new_height) / ORIGIN_HEIGHT
                    new_width = int(ORIGIN_WIDTH * scale)
                    
                    left = new_width / 2 - self.SIZE_LIMITS[size][0] / 2
                    upper = 0
                    right = new_width / 2 + self.SIZE_LIMITS[size][0] / 2
                    lower = new_height
                else:
                    new_width = self.SIZE_LIMITS[size][0]
                    scale = float(new_width) / ORIGIN_WIDTH
                    new_height = int(ORIGIN_HEIGHT * scale)
                    
                    left = 0
                    upper = 0
                    right = self.SIZE_LIMITS[size][0]
                    lower = self.SIZE_LIMITS[size][1]                    
                    
                curimg = img_f.resize((new_width, new_height), 
                                      Image.ANTIALIAS).\
                               crop((left, upper, right, lower))
            # resize for normal sizes
            else:            
                scale = False
                if ORIGIN_WIDTH > self.SIZE_LIMITS[size][0]:
                    new_width = self.SIZE_LIMITS[size][0]
                    scale = float(new_width) / ORIGIN_WIDTH
                else:
                    new_width = ORIGIN_WIDTH
                
                if scale:
                    new_height = int(ORIGIN_HEIGHT * scale)
                else:
                    new_height = ORIGIN_HEIGHT
                    
                if new_height > self.SIZE_LIMITS[size][1]:
                    new_height = self.SIZE_LIMITS[size][1]
                    scale = float(new_height) / ORIGIN_HEIGHT
                    new_width = int(ORIGIN_WIDTH * scale)
                
                curimg = img_f.resize((new_width, new_height), Image.ANTIALIAS)
                
            curpath = '{}_{}.jpg'.format(imgpath_noext, size)    
            #curimg.save(curpath, quality=95, optimize=True)
            curimg.save(curpath, quality=95)
            #curimg.save(curpath)
            setattr(self, 'width_'+size, curimg.size[0])
            setattr(self, 'height_'+size, curimg.size[1])
            
    @classmethod
    def md5sum(cls, file):
        '''
        Calculate md5 sum of given file
        '''
        # md5
        md5 = hashlib.md5()
        
        if file.multiple_chunks():
            for chunk in file.chunks():
                md5.update(chunk)
        else:
            file.seek(0)
            md5.update(file.read())
            
        return md5.hexdigest()
    
    @classmethod
    def from_file(cls, file):
        '''
        Construct an ImageFile from file
        '''
        md5 = cls.md5sum(file)
        
        try:
            imgf = cls.objects.filter(md5=md5).get()
        except ImageFile.DoesNotExist:
            imgf = cls(md5=md5)
            imgf.save()
            
            try:
                imgf.id_str = struk.int2str(imgf.id)
                imgf.file = FieldFile(imgf, imgf.file, imgf.gen_filename())
                imgf.save()
                
                dir = os.path.dirname(imgf.file.path)
                if not os.path.exists(dir):    
                    os.makedirs(dir)
                
                # make sure converted to jpg
                if isinstance(file, InMemoryUploadedFile):
                    tmp = tempfile.NamedTemporaryFile()
                    file.seek(0)
                    tmp.write(file.read())
                    tmp.flush()
                    img = Image.open(tmp.name)
                else: # TemporaryUploadedFile or File
                    img = Image.open(file.file.name)
                
                #img.save(imgf.file.path, quality=95, optimize=True)
                img.save(imgf.file.path, quality=95)
                #img.save(imgf.file.path)
                imgf.width_f = img.size[0]
                imgf.height_f = img.size[1]
                del img
                imgf.resample()
                # save updated width and height of sizes
                imgf.save()
            except:
                imgf.delete()
                raise
        
        return imgf

@receiver(pre_save, sender=ImageFile, 
          dispatch_uid='hypo.models.imagefile_pre_save')
def _imagefile_pre_save(instance, **kwargs):
    ''''''    
    if not instance.created:
        instance.created = time.mktime(datetime.utcnow().timetuple())
        
  
class ImageCopy(models.Model):
    '''
    A reference to ImageFile.
    
    Owned by unique user
    '''
    id_str = models.CharField(max_length=255, unique=True, null=True)
    description = models.CharField(max_length=255)
    # serilzed exif data
    exif_str = models.TextField()
    
    owner = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    #set = models.ForeignKey(ImageSet, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    created = models.PositiveIntegerField()
    
    file = models.ForeignKey(ImageFile)
    
    width_f = property(lambda self: self.file.width_f)
    height_f = property(lambda self: self.file.height_f)
    width_l = property(lambda self: self.file.width_l)
    height_l = property(lambda self: self.file.height_l)
    width_m = property(lambda self: self.file.width_m)
    height_m = property(lambda self: self.file.height_m)
    width_s = property(lambda self: self.file.width_s)
    height_s = property(lambda self: self.file.height_s)
    width_tl = property(lambda self: self.file.width_tl)
    height_tl = property(lambda self: self.file.height_tl)
    width_tm = property(lambda self: self.file.width_tm)
    height_tm = property(lambda self: self.file.height_tm)
    width_ts = property(lambda self: self.file.width_ts)
    height_ts = property(lambda self: self.file.height_ts)
    
    def get_absolute_url(self):
        return '{}images/v/{}/'.format(self.site.uri, self.id_str)
    
    @property
    def uri(self):
        return self.get_absolute_url()
    
    def get_raw_uri(self, size=ImageFile.SIZE_SMALL):
        return self.file.get_uri(size)
    
    @property
    def uri_f(self):
        return self.get_raw_uri(ImageFile.SIZE_FULL)
    
    @property
    def uri_l(self):
        return self.get_raw_uri(ImageFile.SIZE_LARGE)
    
    @property
    def uri_m(self):
        return self.get_raw_uri(ImageFile.SIZE_MEDIAN)
    
    @property
    def uri_s(self):
        return self.get_raw_uri(ImageFile.SIZE_SMALL)
    
    @property
    def uri_tl(self):
        return self.get_raw_uri(ImageFile.SIZE_THUMB_LARGE)
    
    @property
    def uri_tm(self):
        return self.get_raw_uri(ImageFile.SIZE_THUMB_MEDIAN)
    
    @property
    def uri_ts(self):
        return self.get_raw_uri(ImageFile.SIZE_THUMB_SMALL)
    
    @property
    def exif(self):
        return json.loads(self.exif_str)
    
    @property
    def dict(self):
        keys = ['id', 'description', 'exif', 'uri',
               'uri_f', 'uri_l', 'uri_m', 'uri_s', 'uri_tl', 'uri_tm', 'uri_ts',
               'width_f', 'height_f', 'width_l', 'height_l', 
               'width_m', 'height_m', 'width_s', 'height_s',
               'width_tl', 'height_tl', 'width_tm', 'height_tm',
               'width_ts', 'height_ts']
        
        _dict = dict()
        for key in keys:
            try:
                _dict[key] = getattr(self, key)
            except:
                _dict[key] = None
        
        return _dict
        
    @classmethod
    def from_string(cls, data, user, site, desc=''):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(data)
        tmp.flush()
        return cls.from_filename(tmp.name, user, desc)
    
    @classmethod
    def from_filename(cls, filename, user, site, desc=''):
        '''
        Construct an ImageCopy from an filepath
        '''
        return cls.from_file(File(open(filename)), user, desc)
    
    @classmethod
    def from_file(cls, file, user, site, desc=''):
        '''
        Construct an ImageCopy from an uploaded file
        '''
        img = ImageCopy(owner=user, site=site, description=desc)
        
        # strip exif from given image
        file.seek(0)
        exif = pyexiv2.ImageMetadata.from_buffer(file.read())
        exif.read()
        
        exif_dict = dict()
        for k in exif.exif_keys:
            if exif[k].human_value:
                try:
                    exif_dict[exif[k].label] = exif[k].human_value.decode('utf-8')
                except UnicodeDecodeError:
                    # ignore invalid chars
                    pass
            
            del exif[k]
            
        img.exif_str = json.dumps(exif_dict)
            
        img.file = ImageFile.from_file(file)
        img.save()
        
        img.id_str = struk.int2str(img.id)
        img.save()
        
        return img
    
@receiver(pre_save, sender=ImageCopy, 
          dispatch_uid='hypo.models.imagecopy_pre_save')
def _imagecopy_pre_save(instance, **kwargs):
    ''''''    
    if not instance.created:
        instance.created = time.mktime(datetime.utcnow().timetuple())