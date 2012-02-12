from xml.etree import ElementTree
from datetime import datetime, timedelta, tzinfo
import time

from pyrcp.utcdatetime import SimpleTZ, UTCDatetime

from hypo.models import Post

class XMLParser(object):
    ''''''
    @classmethod
    def ns(cls, tag):
        return tag.replace('excerpt:', 
                           '{http://wordpress.org/export/1.0/excerpt/}').\
                   replace('content:', 
                           '{http://purl.org/rss/1.0/modules/content/}').\
                   replace('wfw:', '{http://wellformedweb.org/CommentAPI/}').\
                   replace('dc:', '{http://purl.org/dc/elements/1.1/}').\
                   replace('wp:', '{http://wordpress.org/export/1.0/}')
                   
    @classmethod
    def extract_posts_from_file(cls, file):
        return cls.extract_posts(ElementTree.parse(file))
    
    @classmethod
    def extract_posts(cls, etree):
        e_channel = etree.find('channel')
        if e_channel is None:
            raise Exception('channel node is not found in given etree')
        
        return e_channel.findall('item')
    
    @classmethod
    def extract_title(cls, el, default=''):
        subel = el.find('title')
        if subel is None:
            raise Exception('title node not found in given element')
        
        return subel.text or default
        
    @classmethod
    def extract_text(cls, el):
        subel = el.find(cls.ns('content:encoded'))
        if subel is None:
            raise Exception('content node not found in given element')
        
        return subel.text
    
    @classmethod
    def extract_tags(cls, el):
        tags = set()
        for category in el.findall('category'):
            if 'domain' in category.keys() and 'tag' == category.get('domain'):
                tags.add(category.text)
                
        return tags
    
    @classmethod            
    def extract_datetime(cls, el):             
        subel = el.find('pubDate')
        if subel is not None and subel.text:
            hours = int(subel.text[-5:-2])
            dt = datetime.strptime(subel.text[:-6], '%a, %d %b %Y %H:%M:%S')
            udt = UTCDatetime.from_datetime(dt, hours=hours)
            
            if 0 < udt.timestamp:
                print 'pubdate:', udt.get_local_datetime(hours=8)
                return udt
            
            
        subel = el.find(cls.ns('wp:post_date_gmt'))
        if subel is None or '0000-00-00 00:00:00' == subel.text:
            subel = el.find(cls.ns('wp:post_date'))
            
        dt = datetime.strptime(subel.text, '%Y-%m-%d %H:%M:%S')
        udt = UTCDatetime.from_datetime(dt)
        
        if 0 < udt.timestamp:
            print 'postdate:', udt.get_local_datetime(hours=8)
            return udt