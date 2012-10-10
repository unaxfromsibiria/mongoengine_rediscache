VERSION = (2,0,1)

def install_signals():
    from invalidation import CacheInvalidator
    from config import LazySettings
    from mongoengine import signals
    
    settings = LazySettings()
    
    if settings.content:
        for model_location in settings.scheme:
            location = model_location.split('.')
            model = None
            try:
                if len(location) == 2:
                    exec('from %s import %s as model' % (location[0], location[1]))
                else: # must be 3
                    exec('from %s.%s import %s as model' % (location[0], location[1], location[2]))
            except:
                raise Exception("Can't import document %s from MONGOENGINE_REDISCACHE" % model_location)
    
            signals.post_save.connect(CacheInvalidator.post_save, sender=model)
            signals.post_delete.connect(CacheInvalidator.post_delete, sender=model)

# uncomment for use as Django applications
#install_signals()
