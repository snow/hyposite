from django.db import models
from django.dispatch import receiver

from pyfyd.douban.tasks import Saying, push_saying

from hypo.models import Post, post_to_push

def _len_(str_):
    '''
    string will be encoded before calculating oauth signature
    and douban counts encoded string to limit 280
    so we count string length here
    '''
    return len(str_.encode('utf-8'))

@receiver(post_to_push, sender=Post, 
          dispatch_uid='hypo_douban.models.post_to_push')
def _post_to_push(instance, **kwargs):
    ''''''
    try:
        user = instance.owner
        account = user.doubanaccount_set.all()[0]
    except:
        raise # @todo: 
    else:
        # douban limit saying to 280 char
        # leave 10 char for accidents
        summary_limit = 270 - _len_(instance.title) - _len_(instance.short_uri)
        
        chars = []
        l = 0
        for c in instance.text_summary:
            l += _len_(c)
            chars.append(c)
            if l >= summary_limit:
                # we truncated the string
                chars.append('...')
                break
        summary = ''.join(chars)
        
        content = u'{} {}'.format(summary, instance.short_uri)        
        if instance.title:
            content = u'{}: {}'.format(instance.title, content)
        saying = Saying(content=content)
        
        push_saying.delay(saying, account)
        
