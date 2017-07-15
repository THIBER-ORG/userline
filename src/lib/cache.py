#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import redis

class Cache():
	TYPE_MEM = 0
	TYPE_REDIS = 1

	def __init__(self,rurl=None):
		if rurl is None:
			self.type = self.TYPE_MEM
			self.cache = {}
		else:
			self.type = self.TYPE_REDIS
			self.cache = redis.Redis.from_url(url="redis://:@172.17.0.2:6379/1")
			self.cache.flushdb()

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

		if self.type == self.TYPE_MEM
			try:
				retval = self.cache[name][key]
			except:
				pass
		else:
			retval = cache.get("{}.{}".format(name,key))

		return retval
