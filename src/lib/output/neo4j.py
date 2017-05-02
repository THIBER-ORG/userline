#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import hashlib
from neo4j.v1 import GraphDatabase, basic_auth
from lib.utils import update_relations
from lib.config import CSV_FIELDS

class Neo4J():
	def __init__(self,url):
		proto = "{}/".format('/'.join(url.split('/')[:2]))
		userpwd = url.split('/')[2].split('@')[0]
		uri = url.split('@')[1]
		data = ["{}{}".format(proto,uri),userpwd.split(':')[0], userpwd.split(':')[1]]
		# TODO: Store this relations in a redis-like cache
		self.rels = {'dstrelations':{}, 'domrelations': {},'srcrelations': {},'srcdst':{},'srclogin':{}}

		# setup neo4j
		self.drv = GraphDatabase.driver(data[0], auth=basic_auth(data[1], data[2]))
		self.neo = self.drv.session()
		self.neo.run("CREATE INDEX ON :User(name)")
		self.neo.run("CREATE INDEX ON :Computer(name)")
		self.neo.run("CREATE INDEX ON :Domain(name)")

		# users
		self.sessions = {}

	def __genid_dict(self,value):
		return {'id': "_{}".format(hashlib.sha1("{}".format(value).encode('utf-8')).hexdigest()) , 'name': value }

	def finish(self):
		try:
			self.neo.close()
		except:
			pass

	def __get_logon_data(self,event):
		tmp = ''
		for i in CSV_FIELDS:
			if type(event[i]) == type(int()):
				val = event[i]
			else:
				val = "\"{}\"".format(event[i])
			tmp = "{}, {}: {}".format(tmp,i.replace('.','_'),val)
		return "{{{}}}".format(tmp[1:])


	def __add_domain(self,domain):
		if domain['name'] in ['N/A','MicrosoftAccount','-']:
			return None

		prev = None
		for dom in domain['name'].split('.')[::-1]:
			orig = dom
			dom = self.__genid_dict(dom)

			if prev is None:
				self.neo.run("MERGE ({}:Domain {{name: '{}',label:'{}'}})".format(dom['id'],dom['name'],orig))
				prev = dom['name']
			else:
				self.neo.run("MERGE ({}:Domain {{name: '{}.{}',label:'{}'}})".format(dom['id'],dom['name'],prev,orig))
				self.neo.run("MATCH (subdomain:Domain {{name:'{}.{}'}}),(domain:Domain {{name:'{}'}}) MERGE (subdomain)-[:BELONGS_TO]->(domain)".format(dom['name'],prev,prev))
				prev = "{}.{}".format(dom['name'],prev)


	def __add_computer(self,fqdn,ip=None):
		data = fqdn['name'].split('.')
		name = self.__genid_dict(data[0])

		if ip is None:
			query = "MERGE ({}:Computer {{name: '{}',label:'{}'}})".format(name['id'],fqdn['name'],name['name'])
		else:
			fqdn = self.__genid_dict("{}({})".format(fqdn['name'],ip['name']))
			query = "MERGE ({}:Computer {{name: '{}',label:'{}',ip: '{}'}})".format(name['id'],fqdn['name'],name['name'],ip['name'])

		self.neo.run(query)

		if len(data[1:]) > 0:
			dom = self.__genid_dict('.'.join(data[1:]))
			self.__add_domain(dom)
			self.neo.run("MATCH (computer:Computer {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (computer)-[:MEMBER_OF]->(domain)".format(fqdn['name'],dom['name']))

		return fqdn


	def __add_source_ip(self,ip):
		self.neo.run("MERGE ({}:Computer {{name:'{}',label:'{}'}})".format(ip['id'],ip['name'],ip['name']))
		return ip


	def __add_user(self,user):
		if user['name'] == 'N/A':
			return None
		self.neo.run("MERGE ({}:User {{name: '{}',label:'{}'}})".format(user['id'],user['name'],user['name']))


	def add_sequence(self,event,fullinfo,uniquelogon):
		# add logon source
		username = self.__genid_dict(event['logon.username'])
		computer = self.__genid_dict(event['logon.computer'])
		domain = self.__genid_dict(event['logon.domain'])
		srccomputer = self.__genid_dict(event['logon.srccomputer'])
		srcip = self.__genid_dict(event['logon.srcip'])

		source = None
		if len(event['logon.srcip']) > 0:
			orig = event['logon.srcip']
			if orig in ["127.0.0.1","LOCAL","::1"]:
				source = self.__add_computer(computer)
			elif event['logon.srccomputer'] != 'N/A':
				source = self.__add_computer(srccomputer,srcip)
			else:
				source = self.__add_source_ip(srcip)

		self.__add_user(username)
		self.__add_computer(computer)
		self.__add_domain(domain)

		if username['name'] != 'N/A':
			self.sessions[event['logon.id']] = username

		# check user-computer relation
		exists = False
		if uniquelogon is True:
			try:
				aux = self.rels['dstrelations'][username['id']][computer['id']]
				exists = True
			except:
				exists = False
				self.rels['dstrelations'] = update_relations(self.rels['dstrelations'],{username['id']:{computer['id']: 1}})

		if exists is False:
			if fullinfo is True:
				logondata = self.__get_logon_data(event)
				query = "MATCH (user:User {{name:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {}]->(dest)".format(username['name'],computer['name'],logondata)
			else:
				query = "MATCH (user:User {{name:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {{date:'{}', type: '{}', logonid: '{}', srcid: '{}', src:'{}'}}]->(dest)".format(username['name'],computer['name'],event['logon.datetime'],event['logon.type'],event['logon.id'],event['logon.meta.id'],event['logon.srcip'])

			self.neo.run(query)

		# check user-domain relation
		try:
			aux = self.rels['domrelations'][username['id']][domain['id']]
			exists = True
		except:
			exists = False
			self.rels['domrelations'] = update_relations(self.rels['domrelations'],{username['id']:{domain['id']:1}})
			self.neo.run("MATCH (user:User {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (user)-[:MEMBER_OF]->(domain)".format(username['name'],domain['name']))

		# check src-dst relation
		try:
			aux = self.rels['srcdst'][source['id']][computer['id']]
			exists = True
		except:
			exists = False
			self.rels['srcdst'] = update_relations(self.rels['srcdst'],{source['id']:{computer['id']:1}})
			self.neo.run("MATCH (src:Computer {{name:'{}'}}),(dst:Computer {{name:'{}'}}) MERGE (src)-[:ACCESS_TO]->(dst)".format(source['name'],computer['id']))

		# check user-src relation
		if source is not None:
			try:
				aux = self.rels['srcrelations'][username['id']][source['id']]
				exists = True
			except:
				exists = False
			if exists is False:
				self.rels['srcrelations'] = update_relations(self.rels['srcrelations'],{username['id']: {source['id']:1}})
				self.neo.run("MATCH (src:Computer {{name:'{}'}}),(user:User {{name:'{}'}}) MERGE (user)-[:AUTH_FROM]->(src)".format(source['name'],username['id']))

		# from session (TODO: Only if the source session has been processed. Fixit)
		if event['logon.srcid'] != 'N/A' and event['logon.srcid'] in self.sessions.keys():
			try:
				aux = self.rels['srclogin'][username['id']][event['logon.srcid']]
				exists = True
			except:
				exists = False
			if exists is False:
				self.rels['srcrelations'] = update_relations(self.rels['srclogin'],{username['id']: {event['logon.srcid']:1}})
				self.neo.run("MATCH (dst:User {{name:'{}'}}),(src:User {{name:'{}'}}) MERGE (dst)-[:FROM_SESSION {{logonid:'{}'}}]->(src)".format(username['name'],self.sessions[event['logon.srcid']],event['logon.srcid']))
