VERSION = (2, 0, 2)


def install_signals():
    import importlib
    from invalidation import CacheInvalidator
    from .config import LazySettings
    from mongoengine import signals

    settings = LazySettings()

    if settings.content:
        for model_location in settings.scheme:
            try:
                model = importlib.import_module(model_location)
            except ImportError:
                raise TypeError("Can't import document '{0}' from MONGOENGINE_REDISCACHE"\
                    .format(model_location))

            signals.post_save.connect(
                CacheInvalidator.post_save, sender=model)
            signals.post_delete.connect(
                CacheInvalidator.post_delete, sender=model)

import os


# uncomment for use as Django applications
if os.environ.get('DJANGO_SETTINGS_MODULE'):
    install_signals()
