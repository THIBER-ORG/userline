#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import csv
from lib.config import CSV_FIELDS

class CSV():
	def __init__(self,path):
		# setup csv output
		self.csvwriter = csv.DictWriter(path,fieldnames=CSV_FIELDS,delimiter=',',dialect='excel',quotechar='"',quoting=csv.QUOTE_ALL,escapechar='\\')
		self.csvwriter.writeheader()

	def add_sequence(self,event):
		self.csvwriter.writerow(event)
