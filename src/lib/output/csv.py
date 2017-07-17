#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import csv
from lib.config import CSV_FIELDS,CSV_MARK_POS

class CSV():
	def __init__(self,path):
		# setup csv output
		self.markevt = True
		self.csvwriter = None
		self.csvfields = CSV_FIELDS
		self.path = path

	def add_sequence(self,event):
		if self.csvwriter is None:
			self.csvwriter = csv.DictWriter(self.path,fieldnames=self.csvfields,delimiter=',',dialect='excel',quotechar='"',quoting=csv.QUOTE_ALL,escapechar='\\')
			self.csvwriter.writeheader()
		if self.markevt is False:
			del event['mark.value']
			del event['mark.description']
		self.csvwriter.writerow(event)

	def disable_mark(self):
		self.markevt = False
		count = 0
		for i in CSV_MARK_POS:
			del self.csvfields[i-count]
			count = count + 1

	def finish(self):
		return
