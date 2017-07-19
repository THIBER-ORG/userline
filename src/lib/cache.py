#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import logging
from lib import config

try:
	import redis
	HAVE_REDIS = True
except:
	HAVE_REDIS = False

class Cache():
	TYPE_MEM = 0
	TYPE_REDIS = 1

	log = logging.getLogger(config.APP_NAME)


	def __init__(self,rurl=None):
		if rurl is not None and not HAVE_REDIS:
			self.log.warning("Redis python module not found, using default memory cache")
			rurl = None

		self.__set_cache(rurl)
		if not self.__clear_cache():
			self.log.warning("Redis not available, using default memory cache")
			self.__set_cache(None)


	def __set_cache(self,rurl):
		if rurl is None:
			self.type = self.TYPE_MEM
			self.cache = {}
		else:
			self.type = self.TYPE_REDIS
			self.cache = redis.Redis.from_url(url=rurl)

	def __clear_cache(self):
		if self.type == self.TYPE_REDIS:
			try:
				self.cache.flushdb()
			except:
				return False
		return True

	def create_cache(self,name):
		if self.type == self.TYPE_MEM:
			self.cache[name] = {}
		else:
			pass

	def set_key(self,name,key,val):
		if self.type == self.TYPE_MEM:
			self.cache[name][key] = val
		else:
			self.cache.set("{}.{}".format(name,key),val)

	def get_key(self,name,key):
		retval = None

		if self.type == self.TYPE_MEM:
			try:
				retval = self.cache[name][key]
			except:
				pass
		else:
			val = self.cache.get("{}.{}".format(name,key))
			if type(val) == type(b''):
				val = val.decode('utf-8')
			retval = val

		return retval

	def get_keys(self,name):
		retval = None
		if self.type == self.TYPE_MEM:
			try:
				aux = self.cache[name].keys()
			except:
				return retval
			retval = {}
			for k in aux:
				retval[k] = self.cache[name][k]
		else:
			keys = self.cache.keys("{}.*".format(name))
			retval = {}
			for k in keys:
				name = k.decode('utf-8').split('.')[1:][0]
				retval[name] = self.cache.get(k).decode('utf-8')

		return retval
