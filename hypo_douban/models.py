from django.db import models
from django.dispatch import receiver

from pyfyd.douban.tasks import Saying, push_saying

from hypo.models import Post, post_to_push

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
        content = u'{} {}'.format(instance.text_summary, instance.uri)        
        if instance.title:
            content = u'{}: {}'.format(instance.title, content)
        saying = Saying(content=content)
        
        push_saying.delay(saying, account)
        
