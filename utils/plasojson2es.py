#!/usr/bin/env python3
#
# This is a WIP
#

import sys
import time
import json
from datetime import datetime

def draw_progress_bar(percent, start, prevlen=0,barLen=20):
	progress = ""
	for i in range(barLen):
		aux = int(barLen*percent)
		if i < aux:
			progress += "="
		elif i == aux:
			progress += ">"
		else:
			progress += " "
        
	elapsedTime = time.time() - start;
	estimatedRemaining = int(elapsedTime * (1.0/percent) - elapsedTime)
	msg = "[%s] %.1f%% Elapsed: %im %02is ETA: %im%02is" % (progress, percent * 100, int(elapsedTime)/60, int(elapsedTime)%60, estimatedRemaining/60, estimatedRemaining%60)
	sys.stdout.write("\b"*(prevlen+1))
	sys.stdout.write(msg)
	curlen = len(msg)
	if curlen < prevlen:
		sys.stdout.write(" "*(prevlen-curlen))
	return curlen


def countlines(filename):
	from itertools import (takewhile,repeat)
	f = open(filename, 'rb')
	bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
	ret = sum( buf.count(b'\n') for buf in bufgen )
	f.close()
	return ret

def main():
	global es
	proglen = 0
	totalcount = 0
	total = 0

	if len(sys.argv) != 3:
		print("Usage: {} /input/file /output/file".format(sys.argv[0]))
		return

	#total = countlines(sys.argv[1])
	total = 1872020

	begin = time.time()
	with open(sys.argv[2],'wt') as output:
		with open(sys.argv[1],'rt',encoding = "ISO-8859-1") as events:
			for line in events.readlines():
				count = 0
				for c in line:
					if c != '{':
						count += 1
					elif count > 0:
						break

				line = line[count:]
				try:
					event = json.loads(line)
				except:
					print("Error: {}".format(line))
					continue

				if float(event['timestamp']) < 0:
					continue

				aux = float(str(event['timestamp'])[:-6])
				event['datetime'] = datetime.fromtimestamp(aux).strftime('%Y-%m-%dT%H:%M:%S+00:00')
				totalcount += 1
				output.write(json.dumps(event) + '\r\n')
				proglen = draw_progress_bar(float((totalcount*100/total)/100.0),begin,proglen)
	
if __name__ == "__main__":
	main()
	
