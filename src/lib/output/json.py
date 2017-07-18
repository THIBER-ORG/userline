#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import json
from lib import config

class JSON():
	def __init__(self,fd,duplicate=False):
		self.fd = fd
		self.duplicate = duplicate

	def add_sequence(self,event):
		evt = []

		aux = dict(event)
		for k in list(aux.keys()):
			if aux[k] == 'N/A':
				del aux[k]

		if self.duplicate:
			logout = dict(aux)
			if 'logoff.datetime' in aux.keys():
				logout['datetime'] = aux['logoff.datetime']
				logout['action'] = 'logoff'
			evt.append(logout)
			aux['datetime'] = aux['logon.datetime']
			aux['action'] = 'logon'

		evt.append(aux)

		for i in evt:
			self.fd.write(json.dumps(i,sort_keys=True, indent=config.JSON_INDENT)+'\n')

	def finish(self):
		self.fd.close()
