#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import hashlib
from neo4j.v1 import GraphDatabase, basic_auth
from lib.config import CSV_FIELDS
from lib.cache import Cache

class Neo4J():
	DEST_RELS = 'sequence'
	DOM_RELS = 'domain'
	SRC_RELS = 'source'
	SRCDST_RELS = 'sourcedest'
	SRCLOGIN_RELS = 'srclogin'
	SESSIONS_RELS = 'sessions'
	FROM_SESSIONS = 'fromsessions'
	USER_LIST = 'users'
	DOM_LIST = 'domains'
	SRV_LIST = 'servers'
	SRVDOM_RELS = 'serverbelongsto'

	def __init__(self,url,cache_data):
		proto = "{}/".format('/'.join(url.split('/')[:2]))
		try:
			userpwd = url.split('/')[2].split('@')[0]
		except:
			userpwd = ":"

		try:
			uri = url.split('@')[1]
		except:
			uri = '/'.join(url.split('/')[2:])

		data = ["{}{}".format(proto,uri),userpwd.split(':')[0], userpwd.split(':')[1]]
		# TODO: Store this relations in a redis-like cache
		self.cache = Cache(cache_data)
		self.cache.create_cache(self.DEST_RELS)
		self.cache.create_cache(self.DOM_RELS)
		self.cache.create_cache(self.SRC_RELS)
		self.cache.create_cache(self.SRCDST_RELS)
		self.cache.create_cache(self.SRCLOGIN_RELS)
		self.cache.create_cache(self.SESSIONS_RELS)
		self.cache.create_cache(self.FROM_SESSIONS)
		self.cache.create_cache(self.USER_LIST)
		self.cache.create_cache(self.DOM_LIST)
		self.cache.create_cache(self.SRV_LIST)
		self.cache.create_cache(self.SRVDOM_RELS)

		# setup neo4j
		self.drv = GraphDatabase.driver(data[0], auth=basic_auth(data[1], data[2]))
		self.neo = self.drv.session()
		self.neo.run("CREATE INDEX ON :User(sid)")
		self.neo.run("CREATE INDEX ON :Computer(name)")
		self.neo.run("CREATE INDEX ON :Domain(name)")


	def finish(self):
		try:
			self.neo.close()
		except:
			pass


	def __genid_dict(self,value):
		value = value.strip().upper()
		return {'id': "_{}".format(hashlib.sha1("{}".format(value).encode('utf-8')).hexdigest()) , 'name': value }


	def __gen_key(self,a,b):
		return "{}-{}".format(a.upper(),b.upper())


	def __get_logon_data(self,event):
		tmp = ''
		for i in CSV_FIELDS:
			if type(event[i]) == type(int()):
				val = event[i]
			else:
				val = "\"{}\"".format(event[i])
			tmp = "{}, {}: {}".format(tmp,i.replace('.','_'),val)
		return "{{{}}}".format(tmp[1:])


	def __create_node(self,key,node,query):
		ret = False
		if self.cache.get_key(key,node['id']) is None:
			self.neo.run(query)
			self.cache.set_key(key,node['id'],node['name'])
			ret = True
		return ret


	def __add_domain(self,domain):
		if domain['name'] in ['N/A','MicrosoftAccount','-']:
			return None

		prev = None
		for dom in domain['name'].split('.')[::-1]:
			dom = self.__genid_dict(dom)

			if prev is None:
				self.__create_node(self.DOM_LIST,dom,"MERGE ({}:Domain {{name: '{}',label:'{}'}})".format(dom['id'],dom['name'],dom['name']))
				prev = dom
			else:
				new = self.__genid_dict("{}.{}".format(dom['name'],prev['name']))
				self.__create_node(self.DOM_LIST,new,"MERGE ({}:Domain {{name: '{}',label:'{}'}})".format(new['id'],new['name'],new['name']))
				if self.cache.get_key(self.DOM_LIST,"{}.{}".format(new['id'],prev['id'])) is None:
					self.cache.set_key(self.DOM_LIST,"{}.{}".format(new['id'],prev['id']),True)
					self.neo.run("MATCH (subdomain:Domain {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (subdomain)-[:BELONGS_TO]->(domain)".format(new['name'],prev['name']))
				prev = new


	def __add_computer(self,fqdn,ip=None):
		data = fqdn['name'].split('.')
		name = self.__genid_dict(data[0])

		if ip is None:
			self.__create_node(self.SRV_LIST,fqdn,"MERGE ({}:Computer {{name: '{}',label:'{}'}})".format(name['id'],fqdn['name'],name['name']))
		else:
			fqdn = self.__genid_dict("{}({})".format(fqdn['name'],ip['name']))
			self.__create_node(self.SRV_LIST,fqdn,"MERGE ({}:Computer {{name: '{}',label:'{}',ip: '{}'}})".format(name['id'],fqdn['name'],name['name'],ip['name']))

		if len(data[1:]) > 0:
			dom = self.__genid_dict('.'.join(data[1:]))
			self.__add_domain(dom)
			if self.cache.get_key(self.SRVDOM_RELS,"{}@{}".format(fqdn['id'],dom['id'])) is None:
				self.cache.set_key(self.SRVDOM_RELS,"{}@{}".format(fqdn['id'],dom['id']),True)
				self.neo.run("MATCH (computer:Computer {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (computer)-[:MEMBER_OF]->(domain)".format(fqdn['name'],dom['name']))

		return fqdn


	def __add_source_ip(self,ip):
		self.__create_node(self.SRV_LIST,ip,"MERGE ({}:Computer {{name:'{}',label:'{}'}})".format(ip['id'],ip['name'],ip['name']))
		return ip


	def __add_user(self,user,sid):
		if user['name'] == 'N/A':
			return None
		self.__create_node(self.USER_LIST,sid,"MERGE ({}:User {{name: '{}',sid: '{}',label:'{}'}})".format(sid['id'],user['name'],sid['name'],user['name']))


	def add_sequence(self,event,fullinfo,uniquelogon):
		self.uniquelogon = uniquelogon
		# add logon source
		username = self.__genid_dict(event['logon.username'])
		usersid = self.__genid_dict(event['logon.dstsid'])
		computer = self.__genid_dict(event['logon.computer'])
		domain = self.__genid_dict(event['logon.domain'])
		srccomputer = self.__genid_dict(event['logon.srccomputer'])
		srcip = self.__genid_dict(event['logon.srcip'])

		source = None
		if len(event['logon.srcip']) > 0:
			orig = event['logon.srcip']
			if not orig in ["127.0.0.1","LOCAL","::1","N/A"]:
				if event['logon.srccomputer'] != 'N/A':
					source = self.__add_computer(srccomputer,srcip)
				else:
					source = self.__add_source_ip(srcip)

		self.__add_user(username,usersid)
		self.__add_computer(computer)
		self.__add_domain(domain)

		# for future possible references, store the username
		if username['name'] != 'N/A':
			self.cache.set_key(self.SESSIONS_RELS,event['logon.trackingid'],usersid['name'])

		# check user-computer relation
		exists = None
		if self.uniquelogon is True:
			exists = self.cache.get_key(self.DEST_RELS,self.__gen_key(usersid['id'],computer['id']))
			if exists is None:
				self.cache.set_key(self.DEST_RELS,self.__gen_key(usersid['id'],computer['id']),True)

		if exists is None:
			if fullinfo is True:
				logondata = self.__get_logon_data(event)
				query = "MATCH (user:User {{sid:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {}]->(dest)".format(usersid['name'],computer['name'],logondata)
			else:
				query = "MATCH (user:User {{sid:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {{date:'{}', type: '{}', logonid: '{}', srcid: '{}', trackingid:'{}', src:'{}'}}]->(dest)".format(usersid['name'],computer['name'],event['logon.datetime'],event['logon.type'],event['logon.id'],event['logon.meta.id'],event['logon.trackingid'],event['logon.srcip'])

			self.neo.run(query)

		# check user-domain relation
		exists = self.cache.get_key(self.DOM_RELS,self.__gen_key(usersid['id'],domain['id']))
		if exists is None:
			self.cache.set_key(self.DOM_RELS,self.__gen_key(usersid['id'],domain['id']),True)
			self.neo.run("MATCH (user:User {{sid:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (user)-[:MEMBER_OF]->(domain)".format(usersid['name'],domain['name']))

		# check src-dst relation
		if source is not None:
			exists = self.cache.get_key(self.SRCDST_RELS,self.__gen_key(source['id'],computer['id']))
			if exists is None:
				self.cache.set_key(self.SRCDST_RELS,self.__gen_key(source['id'],computer['id']),True)
				self.neo.run("MATCH (src:Computer {{name:'{}'}}),(dst:Computer {{name:'{}'}}) MERGE (src)-[:ACCESS_TO {{trackingid:'{}'}}]->(dst)".format(source['name'],computer['name'],event['logon.trackingid']))

		# check user-src relation
		if source is not None:
			exists = self.cache.get_key(self.SRC_RELS,self.__gen_key(usersid['id'],source['id']))
			if exists is None:
				self.cache.set_key(self.SRC_RELS,self.__gen_key(usersid['id'],source['id']),True)
				self.neo.run("MATCH (src:Computer {{name:'{}'}}),(user:User {{sid:'{}'}}) MERGE (user)-[:AUTH_FROM {{trackingid:'{}'}}]->(src)".format(source['name'],usersid['name'],event['logon.trackingid']))

		# srctrackingid
		self.cache.set_key(self.FROM_SESSIONS,usersid['name'],event['logon.srctrackingid'])


	def finish(self):
		sessions = self.cache.get_keys(self.FROM_SESSIONS)
		if not sessions:
			return
		for sid in sessions.keys():
			prev = self.cache.get_key(self.SESSIONS_RELS,sessions[sid])
			if prev is not None:
				exists = None
				if self.uniquelogon is True:
					exists = self.cache.get_key(self.SRCLOGIN_RELS,self.__gen_key(sessions[sid],prev))
				if exists is None:
					self.cache.set_key(self.SRCLOGIN_RELS,self.__gen_key(sessions[sid],prev),True)
					self.neo.run("MATCH (cur:User {{sid:'{}'}}),(from:User {{sid:'{}'}}) MERGE (cur)-[:FROM_SESSION {{trackingid:'{}'}}]->(from)".format(sid,prev,sessions[sid]))

		try:
			# https://neo4j.com/developer/python/
			#  File "/usr/local/lib/python3.5/dist-packages/neo4j/v1/api.py", line 245, in _disconnect
			#    self._connection.in_use = False
			#AttributeError: 'NoneType' object has no attribute 'in_use'
			import time
			time.sleep(10)
			self.neo.close()
		except:
			pass
