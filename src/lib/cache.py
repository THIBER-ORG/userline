#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

class Cache():
	def __init__(self):
		self.cache = {}

	def create_cache(self,name):
		self.cache[name] = {}

	def set_key(self,name,key,val):
		self.cache[name][key] = val

	def get_key(self,name,key):
		try:
			return self.cache[name][key]
		except:
			return None
