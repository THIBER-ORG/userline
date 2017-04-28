#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

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
		if domain == 'N/A' or domain == 'MicrosoftAccount' or domain == '-':
			return None
		prev = None
		domain = domain.upper()
		for dom in domain.split('.')[::-1]:
			orig = dom
			dom = dom.replace(' ','_')

			if prev is None:
				self.neo.run("MERGE ({}:Domain {{name: '{}',label:'{}'}})".format(dom,dom,orig))
				prev = dom
			else:
				self.neo.run("MERGE ({}:Domain {{name: '{}.{}',label:'{}'}})".format(dom,dom,prev,orig))
				self.neo.run("MATCH (subdomain:Domain {{name:'{}.{}'}}),(domain:Domain {{name:'{}'}}) MERGE (subdomain)-[:BELONGS_TO]->(domain)".format(dom,prev,prev))
				prev = "{}.{}".format(dom,prev)
		return domain.replace(' ','_')


	def __add_computer(self,fqdn):
		fqdn = fqdn.upper()
		data = fqdn.split('.')
		name = data[0]
		self.neo.run("MERGE ({}:Computer {{name: '{}',label:'{}'}})".format(name,fqdn,name))
		if len(data[1:]) > 0:
			dom = '.'.join(data[1:])
			self.__add_domain(dom)
			self.neo.run("MATCH (computer:Computer {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (computer)-[:MEMBER_OF]->(domain)".format(fqdn,dom))
		return fqdn


	def __add_source_ip(self,ip):
		srcip = "_{}".format(ip.replace('.','_').replace(':','_'))
		self.neo.run("MERGE ({}:Computer {{name:'{}',label:'{}'}})".format(srcip,ip,ip))
		return ip


	def __add_user(self,user):
		if user == 'N/A':
			return None
		username = user.upper()
		usr = username.replace(' ','_').replace('@','').replace('-','_').replace('.','_')
		self.neo.run("MERGE ({}:User {{name: '{}',label:'{}'}})".format(usr,username,user))
		return username


	def add_sequence(self,event,fullinfo,uniquelogon):
		# add logon source
		source = None
		if len(event['logon.srcip']) > 0:
			if event['logon.srcip'] == "127.0.0.1":
				source = event['logon.computer']
				self.__add_computer(source)
			else:
				source = self.__add_source_ip(event['logon.srcip'])

		username = self.__add_user(event['logon.username'])
		computer = self.__add_computer(event['logon.computer'])
		domain = self.__add_domain(event['logon.domain'])

		if username is not None:
			self.sessions[event['logon.id']] = username

		# check user-computer relation
		exists = False
		if uniquelogon is True:
			try:
				aux = self.rels['dstrelations'][username][computer]
				exists = True
			except:
				exists = False
				self.rels['dstrelations'] = update_relations(self.rels['dstrelations'],{username:{computer: 1}})

		if exists is False:
			if fullinfo is True:
				logondata = self.__get_logon_data(event)
				query = "MATCH (user:User {{name:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {}]->(dest)".format(username,computer,logondata)
			else:
				query = "MATCH (user:User {{name:'{}'}}),(dest:Computer {{name:'{}'}}) MERGE (user)-[:LOGON_TO {{date:'{}', type: '{}', logonid: '{}', srcid: '{}', src:'{}'}}]->(dest)".format(username,computer,event['logon.datetime'],event['logon.type'],event['logon.id'],event['logon.meta.id'],event['logon.srcip'])

			self.neo.run(query)

		# check user-domain relation
		try:
			aux = self.rels['domrelations'][username][domain]
			exists = True
		except:
			exists = False
			self.rels['domrelations'] = update_relations(self.rels['domrelations'],{username:{domain:1}})
			self.neo.run("MATCH (user:User {{name:'{}'}}),(domain:Domain {{name:'{}'}}) MERGE (user)-[:MEMBER_OF]->(domain)".format(username,domain))

		# check src-dst relation
		try:
			aux = self.rels['srcdst'][source][computer]
			exists = True
		except:
			exists = False
			self.rels['srcdst'] = update_relations(self.rels['srcdst'],{source:{computer:1}})
			self.neo.run("MATCH (src:Computer {{name:'{}'}}),(dst:Computer {{name:'{}'}}) MERGE (src)-[:ACCESS_TO]->(dst)".format(source,computer))

		# check user-src relation
		if source is not None:
			try:
				aux = self.rels['srcrelations'][username][source]
				exists = True
			except:
				exists = False
			if exists is False:
				self.rels['srcrelations'] = update_relations(self.rels['srcrelations'],{username: {source:1}})
				self.neo.run("MATCH (src:Computer {{name:'{}'}}),(user:User {{name:'{}'}}) MERGE (user)-[:AUTH_FROM]->(src)".format(source,username))

		# from session (TODO: Only if the source session has been processed. Fixit)
		if event['logon.srcid'] != 'N/A' and event['logon.srcid'] in self.sessions.keys():
			try:
				aux = self.rels['srclogin'][username][event['logon.srcid']]
				exists = True
			except:
				exists = False
			if exists is False:
				self.rels['srcrelations'] = update_relations(self.rels['srclogin'],{username: {event['logon.srcid']:1}})
				self.neo.run("MATCH (dst:User {{name:'{}'}}),(src:User {{name:'{}'}}) MERGE (dst)-[:FROM_SESSION {{logonid:'{}'}}]->(src)".format(username,self.sessions[event['logon.srcid']],event['logon.srcid']))
