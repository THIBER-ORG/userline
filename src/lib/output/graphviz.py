#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import hashlib
import graphviz as gv
from lib.cache import Cache

class Graphviz():

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
	

	def __init__(self,output,cache_data):
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
		self.output = output
		self.graph = gv.Digraph()


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

	def __create_node(self,key,node,label):
		ret = False
		if self.cache.get_key(key,node['id']) is None:
			self.graph.node(node['id'],label=label)
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
				self.__create_node(self.DOM_LIST,dom,dom['name'])
				prev = dom
			else:
				new = self.__genid_dict("{}.{}".format(dom['name'],prev['name']))
				self.__create_node(self.DOM_LIST,new,new['name'])
				if self.cache.get_key(self.DOM_LIST,"{}.{}".format(new['id'],prev['id'])) is None:
					self.cache.set_key(self.DOM_LIST,"{}.{}".format(new['id'],prev['id']),True)
					self.graph.edge(new['id'],prev['id'],label='BELONGS_TO')
				prev = new


	def __add_computer(self,fqdn,ip=None):
		data = fqdn['name'].split('.')
		name = self.__genid_dict(data[0])

		if ip is None:
			self.__create_node(self.SRV_LIST,fqdn,fqdn['name'])
		else:
			fqdn = self.__genid_dict("{}({})".format(fqdn['name'],ip['name']))
			self.__create_node(self.SRV_LIST,fqdn,fqdn['name'])

		if len(data[1:]) > 0:
			dom = self.__genid_dict('.'.join(data[1:]))
			self.__add_domain(dom)
			if self.cache.get_key(self.SRVDOM_RELS,"{}@{}".format(fqdn['id'],dom['id'])) is None:
				self.cache.set_key(self.SRVDOM_RELS,"{}@{}".format(fqdn['id'],dom['id']),True)
				self.graph.edge(fqdn['id'],dom['id'],label='MEMBER_OF')

		return fqdn


	def __add_source_ip(self,ip):
		self.__create_node(self.SRV_LIST,ip,ip['name'])
		return ip


	def __add_user(self,user,sid):
		if user['name'] == 'N/A':
			return None
		self.__create_node(self.USER_LIST,sid,user['name'])


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
			if not orig in ["127.0.0.1","LOCAL","::1"]:
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
		if uniquelogon is True:
			exists = self.cache.get_key(self.DEST_RELS,self.__gen_key(usersid['id'],computer['id']))
			if exists is None:
				self.cache.set_key(self.DEST_RELS,self.__gen_key(usersid['id'],computer['id']),True)

		if exists is None:
			self.graph.edge(usersid['id'],computer['id'],label='LOGON_TO')

		# check user-domain relation
		exists = self.cache.get_key(self.DOM_RELS,self.__gen_key(usersid['id'],domain['id']))
		if exists is None:
			self.cache.set_key(self.DOM_RELS,self.__gen_key(usersid['id'],domain['id']),True)
			self.graph.edge(usersid['id'],domain['id'],label='MEMBER_OF')

		# check src-dst relation
		if source is not None:
			exists = self.cache.get_key(self.SRCDST_RELS,self.__gen_key(source['id'],computer['id']))
			if exists is None:
				self.cache.set_key(self.SRCDST_RELS,self.__gen_key(source['id'],computer['id']),True)
				self.graph.edge(source['id'],computer['id'],label='ACCESS_TO')

		# check user-src relation
		if source is not None:
			exists = self.cache.get_key(self.SRC_RELS,self.__gen_key(usersid['id'],source['id']))
			if exists is None:
				self.cache.set_key(self.SRC_RELS,self.__gen_key(usersid['id'],source['id']),True)
				self.graph.edge(usersid['id'],source['id'],label='AUTH_FROM')

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
				self.graph.edge(sid,prev,label="FROM_SESSION")

		self.output.write(self.graph.source)
		self.output.close()
