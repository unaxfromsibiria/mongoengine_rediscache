from base_cache import RedisCache
from django.conf import settings
from invalidation import CacheInvalidator

def install_signals():
    from mongoengine import signals
    for model_location in settings.MONGOENGINE_REDISCACHE.get('scheme'):
        location=model_location.split('.')
        try:
            if len(location) == 2:
                exec('from %s import %s' % (location[0],location[1]))
            else: # must be 3
                exec('from %s.%s import %s' % (location[0],location[1],location[2]))
        except:
            raise Exception("Can't import document %s from MONGOENGINE_REDISCACHE" % model_location)

        try:
            exec("signals.post_save.connect(CacheInvalidator.post_save, sender={0})".format(location[-1]) )
            exec("signals.post_delete.connect(CacheInvalidator.post_delete, sender={0})".format(location[-1]) )
        except:
            pass

install_signals()
