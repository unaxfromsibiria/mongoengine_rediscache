VERSION = (2, 0, 2)


def install_signals():
    import importlib
    from invalidation import CacheInvalidator
    from .config import LazySettings
    from mongoengine import signals, Document

    settings = LazySettings()

    if settings.content:
        for model_location in settings.scheme:
            parts = model_location.split('.')
            modeule_path = '.'.join(parts[:-1])
            try:
                module = importlib.import_module(modeule_path)
            except ImportError:
                raise ImportError("Can't import document '{0}' from MONGOENGINE_REDISCACHE"\
                    .format(model_location))

            model = getattr(module, parts[-1], None)
            if issubclass(model, Document):
                signals.post_save.connect(
                    CacheInvalidator.post_save, sender=model)
                signals.post_delete.connect(
                    CacheInvalidator.post_delete, sender=model)
            else:
                raise ImportError("Can't import document '{0}' from MONGOENGINE_REDISCACHE"\
                    .format(model_location))

import os


# uncomment for use as Django applications
if os.environ.get('DJANGO_SETTINGS_MODULE'):
    install_signals()
