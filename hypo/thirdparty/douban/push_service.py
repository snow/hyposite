#! /usr/bin/env python2.7
# -*- coding: UTF-8 -*-

from os.path import abspath, splitext
from datetime import datetime

from pyrcp.django.cli import setup_env
settings = setup_env(__file__)

from django.contrib.auth.models import User
import hypo.models as hypo
from pyrcp.cliservice import BaseCliService
from pyfyd.douban import OAuthClient2

class PushService(BaseCliService):
    '''Push new posts by users who linked douban account to douban'''
    SAYING_TPL = '''<?xml version='1.0' encoding='UTF-8'?>
<entry xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:db="http://www.douban.com/xmlns/">
<content>{content}</content>
</entry>'''
    
    
    def __init__(self):
        super(PushService, self).__init__()
        self.since_id = None
        self.startup_time = datetime.now()
        
    def get_client(self, key, secret):
        return OAuthClient2(key, secret)
    
    def load_post(self):
        '''Load post that should push tu douban'''
        qs = hypo.Post.objects.filter(author__doubanaccount__isnull=False).\
                               order_by('id')
        if None is self.since_id:
            posts = qs.filter(created__gte=self.startup_time)
        else:        
            posts = qs.filter(id__gt=self.since_id)
            
        try:
            # no use get as there may be more than one post awaiting
            post = posts[0]
            self.since_id = post.id
            return post
        except IndexError:
            print 'no post to push'
            return False
        
    def push(self, post):
        '''push a post to douban'''
        account = post.author.doubanaccount_set.get()
        client = self.get_client(account.key, account.secret)
        
        data = self.SAYING_TPL.format(content=post.output)
        resp, content = client.request('http://api.douban.com/miniblog/saying', 
                                       method='POST', body=data)
        
        if 201 == int(resp['status']):
            pass #done
        else:
            raise Exception('{}: {} when pushing post to douban'.\
                                format(resp['status'], content))
    
    def serve(self):
        post = self.load_post()
        if post:
            self.push(post)
        else:
            return False


if '__main__' == __name__:
    pidfile = '{}.pid'.format(splitext(abspath(__file__))[0])
    PushService.do_cli(pidfile)        