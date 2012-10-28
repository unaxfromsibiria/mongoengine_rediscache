About
=====
:Info: Redis cached tools for caching MongoEngine ORM models
:Author: Michael

Now it better! Version 2 here.

New version contains experience of uses on web-site and upgrades specially for web-projects.

However, there are limitations. I don't recommend to use large selection.

You can use skip() and limits() for exclude this. As often happens, the lists pagination.

Cached selection when length more than 10000 doubtful...

Tried to minimize removing cache, when models change or delete.

What is this?
=====
mongoengine_rediscache allows you create cache on model level,

instead of querying mongo, needed documents would extract from redis.

He can to monitor the relevance of the cache when the model changes (save, update, delete).

Designed for use with or without Django.

Dependencies
=====
- pymongo
- mongoengine
- python-redis
- `blinker <http://pypi.python.org/pypi/blinker#downloads>`_

Usage
=====
You can create models like this (for example look at models.py of application "tests")::

	from mongoengine import *
	from mongoengine import CASCADE as REF_CASCADE
	from mongoengine import PULL as REF_PULL
	from datetime import datetime
	from mongoengine_rediscache.fields import ReferenceFieldCached, ListFieldCached
	from mongoengine_rediscache.queryset import CachedQuerySet
	
	class Model1(Document):
	    name = StringField(max_length=32)
	    volume = IntField()
	    created = DateTimeField(default=datetime.now)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	
	class Model2(Document):
	    name = StringField(max_length=32)
	    count = IntField()
	    created = DateTimeField(default=datetime.now)
	    model1 = ReferenceFieldCached(Model1, reverse_delete_rule=REF_CASCADE, dbref=False)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	
	class Model3(Document):
	    name = StringField(max_length=32)
	    count = IntField()
	    created = DateTimeField(default=datetime.now)
	    model1 = ListFieldCached(ReferenceField(Model1, reverse_delete_rule=REF_CASCADE, dbref=False), required=True)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }

For new mongoengine version accepted dbref=True for reference field.

If you use Django make sure the 'mongoengine_rediscache' after a 'you_application' in INSTALLED_APPS (all your applications)::

	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.sitemaps',
	    'django.contrib.staticfiles',
	    'django.contrib.admin',
	    'packeris',
	    'tests',
	    'webapplication1',
	    'mongoengine_rediscache',
	    'cronis',
	)


Configuration
=====
And more, you must create option in settings::

	MONGOENGINE_REDISCACHE = {
	    'scheme' : {
	                'webapplication1.models.Model1' : { 'all' : 600 },
	                'webapplication1.models.Model2' : { 'count' : 300, 'list' : 300, 'get' : 600 },
	                'webapplication1.models.Model3' : { 'all' : 600 },
	                },
	    'redis' : {
	        'host': 'localhost',
	        'port': 6379,
	        'db'  : 2,
	        'socket_timeout': 5,
	    },
	    'used'      : True,
	    'keyhashed' : 'crc',
	}

- `'count' - use cache for count() method of CachedQuerySet`
- `'list' - use cache in CachedQuerySet, you just need to call property ".cache" after of all "filter" and "order_by"`
- `'reference' - use cache in ReferenceFieldCached`
- `'get' - use cache in CachedQuerySet for all get request`
- `'list_reference' - use cache for ListFieldCached( ReferenceField(Document) )`
Example: list of documents class Model2 will be stored in cache for an 600 seconds.

Posible to use without Django, you'll have such code::

	from mongoengine import *
	from mongoengine import CASCADE as REF_CASCADE
	from mongoengine import PULL as REF_PULL
	from datetime import datetime
	
	from mongoengine_rediscache.config import LazySettings
	from mongoengine_rediscache import install_signals
	from mongoengine_rediscache.queryset import CachedQuerySet
	
	LazySettings.options = {
	    'scheme' : {
	                'models.Model1' : { 'all' : 600 },
	                'models.Model2' : { 'all' : 600 },
	                'models.Model3' : { 'all' : 600 },
	                },
	    'redis' : {
	        'host': 'localhost',
	        'port': 6379,
	        'db'  : 2,
	        'socket_timeout': 5,
	    },
	    'used'      : True,
	    'keyhashed' : 'md5',
	}
	
	class Model1(Document):
	    name = StringField(max_length=32)
	    volume = IntField()
	    created = DateTimeField(default=datetime.now)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	
	class Model2(Document):
	    name = StringField(max_length=32)
	    count = IntField()
	    created = DateTimeField(default=datetime.now)
	    model1 = ReferenceField(Model1, reverse_delete_rule=REF_CASCADE, dbref=False)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	
	class Model3(Document):
	    name = StringField(max_length=32)
	    count = IntField()
	    created = DateTimeField(default=datetime.now)
	    model1 = ListField(ReferenceField(Model1, reverse_delete_rule=REF_CASCADE, dbref=False), required=True)
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	
	install_signals()

I think this all simple..
Easily adapted for use with Flask or any more.

Option 'keyhashed' needed for hashing key in keyspace of redis.

It is known that the optimal length of a redis keys (30-80 bytes) and key hashing usefull for it.

Such values are available: 'md5', 'crc', 'sha1', 'off'

If your mongo collection is not huge, you can use 'crc' (crc32), it fastest.

If 'keyhashed' is 'off' (usefull for debug) then cache name generator will be create keys like this::
  1) "model1:get:pk=507431d618881a29d5489fa6"
  2) "model1:get:pk=507431d618881a29d5489fa7"
  3) "model1:get:pk=507431d618881a29d5489fa8"
  4) "model1:list:_types=Model1|name=regex(64)|created=$lt=2012-10-02 04:23:35|limit=20"
  5) "model1:list:volume=$gt=4587|_types=Model1|created=$lt=2012-10-01 18:39:54|limit=20"
  6) "model1:count:_types=Model1|name=regex(64)|created=$lt=2012-10-02 15:30:11|limit=20"
  7) "model1:count:_types=Model1|name=regex(27)|created=$lt=2012-10-02 15:30:11"
  8) "model1:count:volume=$gt=4932|_types=Model1|name=regex(64)|created=$lt=2012-10-01 18:39:54|limit=20"
  9) "version:model1:_types=Model1|name=regex(64)|created=$lt=2012-10-02 15:30:11|limit=20"

If 'keyhashed' is 'md5' then keys will be hide in hash::
  1) "model1:list:ab202a9082abbf3892f31dccaf00dd86"
  2) "model1:list:7ba456321f5ab1ac1e72291851850222"
  3) "model1:get:5ece9d488ba0d5fd728483641ae98133"
  4) "model1:get:f4fbb8f2d1ba5182cc69ca5483307d8c"
  5) "model1:count:bfa1781b4a91ad188b5e2979377f90e5"
  6) "model1:count:d18324448741ed6a2fcb4918cba9899d"
  7) "model1:count:faea89e7da24e8b7e136b0806df937a9"
  8) "version:model1:c25fe3e908141cf2460c42b47cbd2b58"
  9) "version:model1:48081af7428a47804df03a4b5e8a2f16"

If 'keyhashed' is 'crc' then keys will be hide in crc32::
  1) "model1:list:0x2500dddd"
  2) "model1:list:-0x1a2b98c8"
  3) "model1:list:0x701c7416"
  4) "version:model1"
  5) "version:model1:-0x1a9e8ea6"
  6) "version:model1:0x265a4738"
  7) "model1:get:0x22ef9e6d"
  8) "model1:get:-0x445aa237"
  9) "model1:get:-0x18b616c0"

How to simple flush cahce? It is not necessary run FLUSHALL in redis-cli.

You only can change version of needed collection. For flush cache of Model1 you can::

	redis 127.0.0.1:6379> SELECT 1
	OK
	redis 127.0.0.1:6379[1]> INCRBY "version:model1" 1
	(integer) 12

If you want flush cache for all collection try this::

	$redis-cli -n 1 keys '*version:*' | grep '^version:[a-z0-9]\{1,32\}$' | xargs redis-cli -n 1 incr


Simple tests
=====
OS and soft::

	os: Debian GNU/Linux 3.2.0-3-amd64 x86_64
	cpu: Intel(R) Pentium(R) CPU P6200  @ 2.13GHz
	ram: 5657mb
	redis-server 2.4.14-1
	mongodb 2.0.6-1
	python 2.7.3rc2
	pymongo 2.3
	mongoengine 0.7.4
	redis-py 2.4.13

Here primitive test the speed of documents get::

	=== simple get ===
	---- cache: on ----
	Get test (operations count: 50 000):
	time: 10.1263229847
	time: 9.63664793968
	time: 9.62323498726
	time: 9.86023807526
	
	---- cache: off ----
	Get test (operations count: 50 000):
	time: 52.4118318558
	time: 52.0931260586
	time: 54.8670527935
	time: 54.3389751911
	
	=== getting lists and his length ===
	---- cache: on ----
	Count&List test (operations count: 1000):
	time: 2.64498996735
	object count: 20000
	total lists size 1.220 mb
	time: 2.51725912094
	object count: 20000
	total lists size 1.220 mb
	
	Count&List test (operations count: 10 000):
	time: 27.3708209991
	object count: 200000
	total lists size 12.20 mb
	time: 27.2179660797
	object count: 200000
	total lists size 12.20 mb
	
	---- cache: off ----
	Count&List test (operations count: 1000):
	time: 50.7567090988
	object count: 18361
	total lists size 1.120 mb
	time: 50.4682869911
	object count: 18459
	total lists size 1.126 mb
	
	Count&List test (operations count: 10 000):
	time: 426.830417871
	object count: 200000
	total lists size 12.20 mb
	time: 426.300350904
	object count: 200000
	total lists size 12.20 mb
	
	
	Reference get test (operations count: 10000):
	time: 4.35703992844
	time: 4.46496796608
	time: 3.83190703392
	time: 4.36581397057
	
	---- cache: off ----
	Reference get test (operations count: 10000):
	time: 19.0283870697
	time: 17.5101211071
	time: 18.8498110771
	time: 18.0227570534
	
	=== getting reference list ===
	---- cache: on ----
	Reference list test (operations count: 10000):
	time: 13.4849770069
	total lists size 5.825 mb
	time: 14.1508440971
	total lists size 5.801 mb
	time: 14.4012730122
	total lists size 5.859 mb
	Reference list test (operations count: 10000):
	time: 12.7077980042
	total lists size 5.804 mb
	
	---- cache: off ----
	Reference list test (operations count: 10000):
	time: 46.5085849762
	total lists size 5.823 mb
	time: 48.3886919022
	total lists size 5.807 mb
	time: 19.1344659328
	total lists size 1.220 mb
	time: 45.919934988
	total lists size 5.760 mb

profit there..

Sincerely, Michael Vorotyntsev.
