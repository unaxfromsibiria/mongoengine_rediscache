'''
Created on 19.06.2012

@author: unax
'''

class _queryset_list(list):
    def __init__(self, anylist=None):
        if anylist is None:
            super(_queryset_list, self).__init__()
        else:
            super(_queryset_list, self).__init__(anylist)

    def count(self):
        return len(self)

class SecondaryKey(object):
    key = None
    pk = None
    def __init__(self, key, pk):
        self.key = key
        self.pk = pk
