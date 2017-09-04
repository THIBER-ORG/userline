#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import csv
from lib.config import CSV_FIELDS,CSV_MARK_POS

class Timesketch():
	def __init__(self,path):
		# setup csv output
		self.csvwriter = None
		self.csvfields = ['message','timestamp','datetime','timestamp_desc']
		aux = []
		for col in CSV_FIELDS:
			aux.append(col.replace('.','_'))
		count = 0
		for i in CSV_MARK_POS:
			del aux[i-count]
			count = count + 1
		self.csvfields.extend(aux)
		self.path = path

	def add_sequence(self,event):
		if self.csvwriter is None:
			self.csvwriter = csv.DictWriter(self.path,fieldnames=self.csvfields,delimiter=',',dialect='excel',quotechar='"',quoting=csv.QUOTE_ALL,escapechar='\\')
			self.csvwriter.writeheader()

		del event['mark.value']
		del event['mark.description']

		for i in list(event.keys()):
			if '.' in i:
				aux = i.replace('.','_')
				event[aux] = event[i]
				del event[i]

		#message,timestamp,datetime,timestamp_desc
		event['timestamp'] = event['logon_timestamp']*1000
		event['datetime'] = event['logon_datetime']
		event['timestamp_desc'] = 'logon'
		event['message'] = 'User {}\{} logons to {}'.format(event['logon_domain'],event['logon_username'],event['logon_computer'])
		src = event['logon_srccomputer']
		if src == 'N/A':
			src = event['logon_srcip']
		if not src in ["127.0.0.1","LOCAL","::1","N/A"]:
			event['message'] += " from {}".format(src)

		if len(event['duration']) > 0:
			event['message'] += " (Duration {})".format(event['duration'])

		self.csvwriter.writerow(event)

		if event['logoff_timestamp'] > 0:
			event['timestamp'] = event['logoff_timestamp']*1000
			event['datetime'] = event['logoff_datetime']
			event['timestamp_desc'] = 'logoff'
			event['message'] = 'User {}\{} logoffs from {}'.format(event['logon_domain'],event['logon_username'],event['logon_computer'])
			if len(event['duration']) > 0:
				event['message'] += " (Duration {})".format(event['duration'])
			self.csvwriter.writerow(event)

	def finish(self):
		return
