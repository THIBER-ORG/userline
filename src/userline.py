#!/usr/bin/env python3
#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import sys
import time
import json
import logging
import argparse

from datetime import timedelta,datetime
from dateutil import parser as dateparser

from elasticsearch_dsl import Search,Q,A
from elasticsearch_dsl.connections import connections

from lib import config,defaults,utils
from lib.output.csv import CSV
from lib.output.neo4j import Neo4J
from lib.output.graphviz import Graphviz


def main():

	print("")
	print(" /\ /\  ___  ___ _ __ / /(_)_ __   ___ ")
	print("/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \\")
	print("\ \_/ /\__ \  __/ | / /__| | | | |  __/")
	print(" \___/ |___/\___|_| \____/_|_| |_|\___|  v{}".format(config.VERSION))
	print("")
	print("Author: Chema Garcia (aka sch3m4)")
	print("        @sch3m4")
	print("        https://github.com/thiber-org/userline")
	print("")


	log = logging.getLogger(config.APP_NAME)
	log.setLevel(logging.INFO)
	std = logging.StreamHandler(sys.stdout)
	std.setLevel(logging.INFO)
	formatter = logging.Formatter(config.LOG_FORMAT)
	std.setFormatter(formatter)
	log.addHandler(std)

	parser = argparse.ArgumentParser()

	required = parser.add_argument_group('Required arguments')
	required.add_argument("-H","--eshosts",help="Single or comma separated list of ElasticSearch hosts to query (default: localhost)",default=defaults.ES_HOSTS)
	required.add_argument("-S","--pool-size",help="Connection pool size (default: {})".format(defaults.ES_POOL_SIZE),type=int,default=defaults.ES_POOL_SIZE)
	required.add_argument("-i","--index",help="Index name/pattern",required=True)

	aux = parser.add_argument_group('Actions')
	action = aux.add_mutually_exclusive_group(required=True)
	action.add_argument("-x","--inspect",help="Gets some statistics about the indexed data",action='store_true',default=False)
	action.add_argument("-L","--last-shutdown",help="Gets last shutdown data",action='store_true',default=False)
	action.add_argument("-E","--last-event",help="Gets last event data",action='store_true',default=False)
	action.add_argument("-l","--logons",help="Shows user logon activity",action='store_true',default=False)
	action.add_argument("-w","--who-was-at",help="Shows only logged on users at a given time",metavar="DATE")

	output = parser.add_argument_group('Output')
	output.add_argument("-c","--csv-output",help="CSV Output file",type=argparse.FileType('w'),metavar="PATH")
	output.add_argument("-n","--neo4j",help="Neo4j bolt with auth (format: bolt://user:pass@host:port)",metavar="BOLT")
	output.add_argument("-g","--graphviz",help="Graphviz .dot file",type=argparse.FileType('w'),metavar="PATH")

	csvout = parser.add_argument_group('CSV options')
	csvout.add_argument("-F","--disable-timeframe",help="Do not create timeframe entries",action='store_true',default=False)

	neoargs = parser.add_argument_group('Neo4J options')
	neoargs.add_argument("-f","--neo4j-full-info",help="Saves full logon/logoff info in Neo4j relations",action='store_true',default=False)

	graphargs = parser.add_argument_group("Graph (Neo4J/Graphviz) options")
	graphargs.add_argument("-s","--unique-logon-rels",help="Sets unique logon relations",action='store_true',default=False)

	optional = parser.add_argument_group('Optional filtering arguments')
	optional.add_argument("-t","--min-date",help="Searches since specified date (default: {})".format(defaults.MIN_DATE),default=defaults.MIN_DATE)
	optional.add_argument("-T","--max-date",help="Searches up to specified date (default: {})".format(defaults.MAX_DATE),default=defaults.MAX_DATE)
	optional.add_argument("-p","--pattern",help="Includes pattern in search")
	optional.add_argument("-I","--include-local",help="Includes local services logons (default: Excluded)",action='store_true', default=False)
	optional.add_argument("-k","--include-locks",help="Includes workstation/screensaver lock events (default: Excluded)",action='store_true', default=False)
	optional.add_argument("-v","--verbose",help="Enables verbose mode",action='store_true',default=False)

	extrainfo = parser.add_argument_group('Extra information')
	extrainfo.add_argument("-m","--mark-if-logged-at",help="Marks logged in users at a given time",metavar="DATETIME")

	args = parser.parse_args()

	if args.last_event is False and args.logons is False and args.who_was_at is None and args.last_shutdown is False and args.inspect is False:
		log.critical("You need to specify at least one action argument")
		return

	if args.verbose is True:
		log.setLevel(logging.DEBUG)
		std.setLevel(logging.DEBUG)

	try:
		mindate = int(dateparser.parse(args.min_date).timestamp()*10**3)
		maxdate = int(dateparser.parse(args.max_date).timestamp()*10**3)
		if args.who_was_at is not None:
			whowasat = int(dateparser.parse(args.who_was_at).timestamp()*10**3)
		if args.mark_if_logged_at is not None:
			whowasat = int(dateparser.parse(args.mark_if_logged_at).timestamp()*10**3)
	except Exception as exc:
		log.critical("Error parsing date: {}".format(exc))
		return

	# setup elasticsearch
	connections.create_connection(hosts=args.eshosts.split(','),maxsize=args.pool_size)
	conn = connections.get_connection()

	# shows some statistics about the indexed data
	if args.inspect is True:
		stats = utils.get_statistics(args.index,args.pattern)
		log.info("Statistics:")
		log.info("\t- Computers:      {}".format(stats['computers']))
		log.info("\t- Src usernames:  {}".format(stats['srcuser']))
		log.info("\t- Dst usernames:  {}".format(stats['dstuser']))
		log.info("\t- Dst computers:  {} by name".format(stats['dstsrvname']))
		log.info("\t- Dst computers:  {} by IP".format(stats['dstsrvip']))
		log.info("\t- Total events:   {}".format(stats['total']))
		return

	# shows last shutdown
	if args.last_shutdown is True:
		aux = utils.get_last_shutdown(args.index,maxdate,args.pattern)
		if aux is not None:
			log.info("Last shutdown:")
			for k in aux.keys():
				item = aux[k]
				evt = utils.build_event_from_source(item)
				lastraw = utils.get_last_event(args.index,evt['computer'],maxdate)
				lastevt = utils.build_event_from_source(lastraw)
				uptime = timedelta(microseconds=(lastevt['timestamp'] - evt['timestamp'])*10**3)
				log.info("Computer: {}".format(evt['computer']))
				log.info("\t- Datetime: {}".format(evt['datetime']))
				log.info("\t- Uptime:   {}".format(uptime))
				log.info("\t- EvtIndex: {}".format(evt['index']))
				log.info("\t- EvtId:    {}".format(evt['sourceid']))
		else:
			log.info("No shutdown found")
		return

	# shows last stored event
	if args.last_event is True:
		aux = utils.get_last_event(args.index,computer=None,maxdate=maxdate,pattern=args.pattern)
		if aux is not None:
			log.info("Last event:")
			for k in aux.keys():
				lastevt = utils.build_event_from_source(aux[k])
				log.info("Computer: {}".format(lastevt['computer']))
				log.info(json.dumps(lastevt,sort_keys=True,indent=4))
		else:
			log.info("No events found")
		return

	# we need an output format
	if args.csv_output is None and args.neo4j is None and args.graphviz is None:
		log.critical("This option requires CSV/Neo4J/Graphviz output")
		return

	csv = None
	if args.csv_output is not None:
		csv = CSV(args.csv_output)
		if args.mark_if_logged_at is None:
			csv.disable_mark()

	neo = None
	if args.neo4j is not None:
		neo = Neo4J(args.neo4j)

	graph = None
	if args.graphviz is not None:
		graph = Graphviz(args.graphviz)

	log.info("Building query")
	# Look for first required events
	q = Q('match',data_type='windows:evtx:record') & utils.get_dsl_logon_query(args.include_locks)

	if args.pattern is not None:
		q = q & Q('query_string',query=args.pattern,analyze_wildcard=True)

	s = Search(using=conn, index=args.index).query(q).filter('range',datetime={'gte':mindate,'lte':maxdate}).sort('datetime')

	log.debug("Getting events count")
	total = s.execute().hits.total
	log.info("Found {} events to be processed".format(total))

	# timeframe
	if total > 0 and csv is not None and args.disable_timeframe is False:
		frame = dict(config.EVENT_STRUCT)
		for k in frame.keys():
			frame[k] = "-"*10
		frame[config.CSV_FIELDS[0]] = "TIMEFRAME/START"
		frame['logon.datetime'] = args.min_date
		frame['logon.timestamp'] = mindate
		frame['logoff.datetime'] = args.min_date
		frame['logoff.timestamp'] = mindate
		csv.add_sequence(frame)

	count = 0
	proglen = 0
	progress = 0
	begin = time.time()
	log.info("Processing events")
	for hit in s.scan():
		login = utils.build_event_from_source(hit)
		log.debug("Got logon event: {}".format(login['id']))
		duration = ''
		logout = None

		# local service check
		if args.include_local is False and ( \
							login['domain'] == config.LOCAL_DOMAIN or \
							login['username'].upper() == "{}$".format(login['computer'].split('.')[0]).upper() or \
							login['logonid'] == config.CONSTANT_NA \
						):
			discard = True
			log.debug("Discarding event")

		# workstation/screensaver locks
		elif args.include_locks is False and login['type'] == config.LOGON_TYPE_UNLOCK:
			discard = True
			log.debug("Discarding event")
		else:
			aux = utils.get_logout_event(args.index,login['logonid'],login['timestamp'],maxdate,args.include_locks)
			logout = utils.build_event_from_source(aux)
			log.debug("Got logoff event for login id {}".format(login['id']))

			if logout['timestamp'] > 0:
				aux = logout['timestamp'] - login['timestamp']
				try:
					duration = str(timedelta(microseconds=aux*10**3))
				except:
					duration = '-'

			event = utils.build_logon_sequence(duration,login,logout)
			if logout is not None:
				log.debug("Logon sequence complete")

			if args.mark_if_logged_at is not None:
				event['mark.description'] = "Logged on at {}".format(args.mark_if_logged_at)
				if login['timestamp'] > whowasat or (logout['timestamp'] > 0 and logout['timestamp'] < whowasat):
					event['mark.value'] = False
				else:
					event['mark.value'] = True

			discard = False
			if args.who_was_at is not None and (login['timestamp'] > whowasat or (logout['timestamp'] > 0 and logout['timestamp'] < whowasat)):
				discard = True
				log.debug("Discarding event")

		if discard is False:
			count += 1
			if csv is not None:
				csv.add_sequence(event)
			if neo is not None:
				neo.add_sequence(event,args.neo4j_full_info,args.unique_logon_rels)
			if graph is not None:
				graph.add_sequence(event,args.neo4j_full_info,args.unique_logon_rels)
			log.debug("Event stored")

		progress += 1
		proglen = utils.draw_progress_bar(float((progress*100/total)/100.0),begin,proglen)

	# timeframe
	if total > 0 and csv is not None and args.disable_timeframe is False:
		frame = dict(config.EVENT_STRUCT)
		for k in frame.keys():
			frame[k] = "-"*10
		frame[config.CSV_FIELDS[0]] = "TIMEFRAME/END"
		frame['logon.datetime'] = args.max_date
		frame['logon.timestamp'] = maxdate
		frame['logoff.datetime'] = args.max_date
		frame['logoff.timestamp'] = maxdate
		csv.add_sequence(frame)

	total = timedelta(microseconds=int((time.time() - begin)*10**6))
	print("")
	log.info("{} Logons processed in {}".format(count,total))

	if neo is not None:
		neo.finish()
	if graph is not None:
		graph.finish()

	return


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass

