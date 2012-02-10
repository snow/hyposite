import cgi
import json
import hashlib
import os
from datetime import datetime
import tempfile
import re
from urllib2 import quote

from BeautifulSoup import BeautifulSoup 
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models.fields.files import FieldFile
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.dispatch import receiver
from django import forms
from PIL import Image
import pyexiv2 
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
    
    @property    
    def primary_site(self):
        return Site.objects.get(owner=self.user, is_primary=True)
    
    def has_perm(self, object, perm=''):
        if isinstance(object, Site):
            return object.owner == self.user
        elif isinstance(object, Post):
            return object.site.owner == self.user
        
        return False
    
@receiver(post_save, sender=User, 
          dispatch_uid='hypo.models.create_user_profile')
def _create_user_profile(instance, created, **kwargs):
    '''Create empty user profile on user model created'''
    if created:
        profile = UserProfile(user=instance)
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
        return '/site/{}/'.format(self.slug)
    
    @classmethod
    def from_request(cls, request):
        matches = re.match('/site/([-\w]+)/', request.path_info)
        if matches:
            slug = matches.groups()[0]
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
    
#class SiteChoiceField(forms.ModelChoiceField):
#    ''''''
#    def __init__(self, user, *args, **kwargs):
#        queryset = Site.objects.filter(owner=user)
#        super(SiteChoiceField, self).__init__(queryset, *args, **kwargs)


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
    slug = forms.SlugField(max_length=255)
    title = forms.CharField(max_length=255)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login', 'date_joined')         
        
        
#class Entry(models.Model):
#    '''super class of article, image set, status and so on'''
#    id_str = models.CharField(max_length=255, default='')
#    owner = models.ForeignKey(User)
#    site = models.ForeignKey(Site)
#    
##    T_ARTICLE = 1
##    T_IMAGE_SET = 2
##    TYPES = {
##        T_ARTICLE: 'article',
##        T_IMAGE_SET: 'image_set'
##    }    
##    type = models.PositiveSmallIntegerField(choices=TYPES.items(), null=True)
#    
#    created = models.DateTimeField(auto_now_add=True)
#    updated = models.DateTimeField(auto_now=True)
#    
#    source = models.URLField(null=True, blank=True)
#    
#    def __init__(self, *args, **kwargs):
#        super(Entry, self).__init__(*args, **kwargs)
#        #self.__ext_attrs = {}
#        self.__sub_object = None
#    
#    def __get_sub_object(self):
#        if not self.__subobject:        
#            if self.T_ARTICLE == self.type:
#                self.__sub_object = self.article
#            elif self.T_IMAGE_SET == self.type:
#                self.__sub_object = self.imageset
#            else:
#                raise NotImplemented()
#            
#        return self.__sub_object
#    
#    def __get_sub_attr(self, attr, default=None):
#        return getattr(self.__get_sub_object(), attr, default)
#        
#    @property
#    def uri(self):
#        return self.__get_sub_attr('uri')
#    
#    @property
#    def title(self):
#        return self.__get_sub_attr('title', '')
#    
#    @property
#    def summary(self):
#        return self.__get_sub_attr('summary', '')
#    
#    @property
#    def text(self):
#        return self.__get_sub_attr('text', '')
#    
##    
##    def get_imgs(self):
##        return []
#    
#@receiver(post_save, sender=Entry, 
#          dispatch_uid='hypo.models.assign_entry_id_str')
#def _assign_entry_id_str(instance, created, **kwargs):
#    '''Create empty user profile on user model created'''
#    if '' == instance.id_str:
#        instance.id_str = struk.int2str(instance.id)
#        instance.save()
        
class Post(models.Model):
    '''A post may contain title, text content and images'''    
    id_str = models.CharField(max_length=255)
    slug = models.SlugField() # used in url as descript, it is NOT unique
    
    title = models.CharField(max_length=30, blank=True)
    
    text_source = models.TextField()
    text_summary = models.CharField(max_length=140, blank=True)
    text = models.TextField(blank=True)
    
    images = models.ManyToManyField('ImageCopy')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    site = models.ForeignKey(Site)
#    F_PLAIN = 0str to url
#    F_HTML = 1
#    F_MARKDOWN = 2
#    FORMATS = {
#        F_PLAIN: 'plain',
#        F_HTML: 'html',
#        F_MARKDOWN: 'markdown',
#    }
#    format = models.PositiveSmallIntegerField(choices=FORMATS.items(), 
#                                              default=F_PLAIN)
    
    
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
    
    
#    def modify_content(self, source, format):
#        self.content_source = source
#        self.format = format
#        
#        if self.F_PLAIN == self.format:
#            self.content, self.content_summary = \
#                self.process_plain_content_source(source)
#        elif self.F_HTML == self.format:
#            self.content, self.content_summary = \
#                self.process_html_content_source(source)
#        else:
#            raise NotImplemented()
#        
#    def get_content_format(self):
#        return self.FORMATS[self.format]       
    
    def get_absolute_url(self):
        return '{}posts/v/{}/{}/'.format(self.site.uri, self.id_str, self.slug)
    
    @property
    def uri(self):
        return self.get_absolute_url()
    
    @property
    def summary(self):
        return self.text_summary
    
#    @classmethod
#    def create(cls, user, site, content_source, title=''):    
#        try:
#            entry = Entry(owner=user, site=site, type=Entry.T_ARTICLE)
#            entry.save()
#            
#            article = cls(entry=entry, title=title, 
#                          content_source=content_source)
#            #article.modify_content(content_source, format)
#            article.save()
#            
#            return article
#        except Exception as err:
#            try:
#                article.delete()
#            except:
#                pass  
#            
#            try:
#                entry.delete()
#            except:
#                pass                
#            
#            raise err
        
#    @classmethod
#    def process_plain_content_source(cls, source):
#        content = cgi.escape(source)
#        summary = cls.extract_content_summary(content)
#        
#        return (content, summary)

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
        summary = str(content)
        
        if 137 < len(summary):
            return '{}...'.format('\n'.join(summary[:137].split('\n')[:10]))
        else:
            return ''

@receiver(pre_save, sender=Post, dispatch_uid='hypo.models.post_pre_save')
def _post_pre_save(instance, **kwargs):
    '''Create empty user profile on user model created'''
    instance.text, content_plain, instance.text_summary = \
        Post.process_html_content_source(instance.text_source)
        
    slug = instance.title or instance.text_summary or content_plain
    instance.slug = quote(slug.strip()[:50].replace(' ', '_'))
    
@receiver(post_save, sender=Post, 
          dispatch_uid='hypo.models.post_post_save')
def _post_post_save(instance, created, **kwargs):
    ''''''
    if not instance.id_str:
        instance.id_str = struk.int2str(instance.id)
        instance.save()
        
        
class PostForm(forms.ModelForm):
    ''''''
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
    created = models.DateTimeField(auto_now_add=True)
    
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
        #l = logging.getLogger('c')
        #l.debug(uri)
        
        if self.SIZE_FULL == size:
            return uri
        else:
            path, ext = os.path.splitext(uri)
            #l.debug(path)
            #l.debug(ext)
            #l.debug(''.join(('{}_{}'.format(path, size), ext)))
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


#class ImageSet(Entry):
#    '''
#    Image set
#    '''
#    description = models.TextField()
#    is_temp = models.BooleanField(default=True)
#    
#    article = models.ForeignKey(Article, unique=True, null=True, blank=True)
#    
#    @property
#    def title(self):
#        return self.description[:20]
#    
#    @property
#    def uri(self):
#        uri = '{}image_sets/{}/'.format(self.site.uri, self.id_str)
#        if self.title:
#            uri = '{}{}/'.format(uri, self.title)
#            
#        return uri    
#    
#    @property
#    def text(self):
#        return self.description
#    
#    @property
#    def summary(self):
#        return self.title 
    
#    @classmethod
#    def create(cls, user, site, description='', article=None, is_temp=True):    
#        try:
#            entry = Entry(owner=user, site=site, type=Entry.T_IMAGE_SET)
#            entry.save()
#            
#            set = cls(description=description, is_temp=is_temp, entry=entry, 
#                      article=article)
#            #article.modify_content(content_source, format)
#            set.save()
#            
#            return set
#        except Exception as err:
#            try:
#                set.delete()
#            except:
#                pass  
#            
#            try:
#                entry.delete()
#            except:
#                pass                
#            
#            raise err
#class Tag(models.Model):
#    '''
#    Tag
#    '''
#    text = models.CharField(max_length=255, unique=True)
#    created = models.DateTimeField(auto_now_add=True)
#@receiver(post_save, sender=ImageSet, 
#          dispatch_uid='hypo.models.imageset_post_save')
#def _imageset_post_save(instance, created, **kwargs):
#    ''''''
#    if created:
#        entry = instance.entry_ptr
#        entry.type = Entry.T_IMAGE_SET
#        entry.save()
  
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
    #tags = models.ManyToManyField(Tag, related_name='images')
    created = models.DateTimeField(auto_now_add=True)
    
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
    
    def get_raw_uri(self, size=ImageFile.SIZE_SMALL):
        return self.file.get_uri(size)
    
    @property
    def uri(self):
        return '{}images/{}/'.format(self.site.uri, self.id_str)
    
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