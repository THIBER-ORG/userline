# UserLine

This tool automates the process of creating logon relations from MS Windows Security Events by showing a graphical relation among users domains, source and destination logons as well as session duration.

![](https://raw.githubusercontent.com/thiber-org/userline/master/img/graph.png)

It has three output modes:
1. Standard output
1. CSV file
1. Neo4J graph
1. Graphviz dot file

# Content
1. [Preparation](#preparation)
    1. [Building a docker image](#building-a-docker-image)
    1. [Running from docker](#running-from-docker)
1. [Command Line](#command-line)
1. [EVTx Analisys](#evtx-analisys)
1. [Indexing](#indexing)
1. [Using the tool](#using-the-tool)
1. [CSV Output](#csv-output)
1. [Neo4J Export](#neo4j-export)
    1. [Querying Neo4J data](#querying-neo4j-data)
    1. [Removing Neo4J data](#removing-neo4j-data)
1. [Graphviz dot file output](#graphviz-dot-file-output)
    1. [Image generation from graph .dot file](#image-generation-from-graph-dot-file)
    1. [Import graph into Gephi](#import-graph-into-gephi)
1. [SQLite import](#sqlite-import)
1. [Processed events](#processed-events)

## Preparation
	git clone https://github.com/THIBER-ORG/userline.git
	cd userline/src
	sudo pip3 install -U -r requirements.txt

### Building a docker image
Optionally you can build a docker image as follows:

	git clone https://github.com/THIBER-ORG/userline.git
	cd userline
	docker build . -t userline

### Running from docker
To work with UserLine when using the docker image, use the following syntax:

	docker run --rm -ti --net=host -v [YOUR_DATA_PATH]:/data userline userline [PARAMETERS]

Example:

	docker run --rm -ti --net=host -v $(pwd)/data:/data userline userline -h

**Note**: ``--net=host`` is only required if you're running ElasticSearch/Neo4J in another container on the same host.

## Command line

	$ ./userline.py -h
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	usage: userline.py [-h] [-H ESHOSTS] [-S POOL_SIZE] -i INDEX
	                   (-L | -E | -l | -w DATE) [-c PATH] [-n BOLT] [-g PATH] [-F]
	                   [-f] [-s] [-t MIN_DATE] [-T MAX_DATE] [-p PATTERN] [-I]
	                   [-k] [-v] [-m DATETIME]
	
	optional arguments:
	  -h, --help            show this help message and exit
	
	Required arguments:
	  -H ESHOSTS, --eshosts ESHOSTS
	                        Single or comma separated list of ElasticSearch hosts
	                        to query (default: localhost)
	  -S POOL_SIZE, --pool-size POOL_SIZE
	                        Connection pool size (default: 5)
	  -i INDEX, --index INDEX
	                        Index name/pattern
	
	Actions:
	  -L, --last-shutdown   Gets last shutdown data
	  -E, --last-event      Gets last event data
	  -l, --logons          Shows user logon activity
	  -w DATE, --who-was-at DATE
	                        Shows only logged on users at a given time
	
	Output:
	  -c PATH, --csv-output PATH
	                        CSV Output file
	  -n BOLT, --neo4j BOLT
	                        Neo4j bolt with auth (format:
	                        bolt://user:pass@host:port)
	  -g PATH, --graphviz PATH
	                        Graphviz .dot file
	
	CSV options:
	  -F, --disable-timeframe
	                        Do not create timeframe entries
	
	Neo4J options:
	  -f, --neo4j-full-info
	                        Saves full logon/logoff info in Neo4j relations
	
	Graph (Neo4J/Graphviz) options:
	  -s, --unique-logon-rels
	                        Sets unique logon relations
	
	Optional filtering arguments:
	  -t MIN_DATE, --min-date MIN_DATE
	                        Searches since specified date (default: 2016-05-04)
	  -T MAX_DATE, --max-date MAX_DATE
	                        Searches up to specified date (default: 2017-05-04)
	  -p PATTERN, --pattern PATTERN
	                        Includes pattern in search
	  -I, --include-local   Includes local services logons (default: Excluded)
	  -k, --include-locks   Includes workstation/screensaver lock events (default:
	                        Excluded)
	  -v, --verbose         Enables verbose mode
	
	Extra information:
	  -m DATETIME, --mark-if-logged-at DATETIME
	                        Marks logged in users at a given time

## EVTx Analisys

Analyze EVTx files with [plaso](https://github.com/log2timeline/plaso)

	$ docker run -v /mnt/IR/1329585/:/data log2timeline/plaso log2timeline --hashers md5,sha256 -z Europe/Madrid /data/processed/events/windows/security/sec-evtx.plaso /data/evidences/events/windows/security/


## Indexing

**Note**: psort elastic output is really slow, for better performance upload the .plaso file to [TimeSketch](https://github.com/google/timesketch)

If your image does not already support it, enable elastic output psort module

	$ docker run -ti --entrypoint=/bin/bash -v /mnt/IR/1329585/:/data log2timeline/plaso
	root@@d3a8d0e1f0ac:/home/plaso# apt-get update && apt-get install -y python-pip && pip install pyelasticsearch

Process the events and store them into elasticsearch

	root@@d3a8d0e1f0ac:/home/plaso# psort.py -o elastic --server 172.21.0.2 --port 9200 --doc_type plaso --index_name ir-1329585-events-security-windows /data/processed/events/windows/security/sec-evtx.plaso


## Using the tool

Getting the last shutdown event:

	$ ./userline.py -i ir-1329585-events-security-windows --last-shutdown
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Last shutdown:
	INFO - Computer: ws01.evil.corp
	INFO - 	- Datetime: 2016-07-12 18:56:33+00:00
	INFO - 	- Uptime:   124 days, 23:24:03
	INFO - 	- EvtIndex: ir-1329585-events-security-windows
	INFO - 	- EvtId:    AVsRMBloEoASMdQErSf-

Getting the last event:

	$ ./userline.py -i ir-1329585-events-security-windows --last-event
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Last event:
	INFO - Computer: ws01.evil.corp
	INFO - {
	    "computer": "ws01.evil.corp",
	    "datetime": "2017-02-14 05:04:36+00:00",
	    "description": "N/A",
	    "domain": "N/A",
	    "eventid": 6006,
	    "id": "cbc2794961fa5ced4366ef52673479faf4df5a53ca66280263526bbe0bee13af",
	    "index": "ir-1329585-events-security-windows",
	    "ipaddress": "N/A",
	    "logonid": "N/A",
	    "raw": "<Event xmlns=\"http://schemas.microsoft.com/win/2004/08/events/event\">\n  <System>\n    <Provider Name=\"EventLog\"/>\n    <EventID Qualifiers=\"32768\">6006</EventID>\n    <Level>4</Level>\n    <Task>0</Task>\n    <Keywords>0x0080000000000000</Keywords>\n    <TimeCreated SystemTime=\"2017-02-14T05:44:36.000000000Z\"/>\n    <EventRecordID>784</EventRecordID>\n    <Channel>System</Channel>\n    <Computer>ws01.evil.corp</Computer>\n    <Security/>\n  </System>\n  <EventData>\n    <Binary>0100000000000000</Binary>\n  </EventData>\n</Event>\n",
	    "sourceid": "AOsBX5IrkRtSdYVCbxr4",
	    "srcid": "N/A",
	    "timestamp": 1492458753000,
	    "type": "N/A",
	    "username": "N/A"
	}

## CSV Output
Getting logon relations between two dates into a CSV file:

	$ ./userline.py -l -i ir-1329585-events-security-windows -t 2016-11-20T11:00:00 -T 2016-11-21T11:00:00 -c output.csv
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Building query
	INFO - Found 297 events to be processed
	INFO - Processing events
	[====================] 100.0% Elapsed: 0m 02s ETA: 0m00s
	INFO - 44 Logons processed in 0:00:02.051880

## Neo4J Export

Getting logon relations into Neo4J graph:

	$ docker run -d -p 7474:7474 -p 7687:7687 -v $HOME/neo4j/data:/data neo4j
	$ ./userline.py -l -i ir-1329585-events-security-windows -t 2016-11-20T11:00:00 -T 2016-11-21T11:00:00 -n "bolt://user:pass@172.17.0.2:7687/"
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Building query
	INFO - Found 297 events to be processed
	INFO - Processing events
	[====================] 100.0% Elapsed: 0m 02s ETA: 0m00s
	INFO - 44 Logons processed in 0:00:02.051880

### Querying Neo4J data

	MATCH(n) RETURN(n)
	
Query the results using Neo4J CQL

![](https://raw.githubusercontent.com/thiber-org/userline/master/img/result.png)

### Removing Neo4J data

	MATCH(n)-[r]-(m) DELETE n,r,m
	MATCH(n) DELETE n
	
## Graphviz dot file output

	$ ./userline.py -l -i ir-1329585-events-security-windows -t 2016-11-20T11:00:00 -T 2016-11-21T11:00:00 -g graph.dot
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.3b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Building query
	INFO - Found 297 events to be processed
	INFO - Processing events
	[====================] 100.0% Elapsed: 0m 02s ETA: 0m00s
	INFO - 44 Logons processed in 0:00:02.051880

### Image generation from graph .dot file

Once you've generated the .dot file, you can generate an image with the graph as follows:

	$ dot -Tpng graph.dot > graph.png

### Import graph into Gephi

Once you've generated the .dot file, you can import the graph into [Gephi](https://gephi.org/):

![](https://raw.githubusercontent.com/thiber-org/userline/master/img/gephi.1.png)

## SQLite Import

Once you've generated the CSV output, you can import the data into a SQLite database and query the data through SQL queries:

	$ sqlite3 logon.db
	SQLite version 3.11.0 2016-02-15 17:29:24
	Enter ".help" for usage hints.
	sqlite> .mode csv userline
	sqlite> .import output.csv userline
	sqlite> .tables
	userline
	sqlite> .q
	$ sqliteman logon.db

![](https://raw.githubusercontent.com/thiber-org/userline/master/img/sqliteman.png)

## Processed events
### Logon events
- EVENT_WORKSTATION_UNLOCKED = 4801
- EVENT_SCREENSAVER_DISMISSED = 4803
- EVENT_LOGON = 4624
- EVENT_LOGON_EXPLICIT = 4648
- EVENT_SESSION_RECONNECTED = 4778

### Logoff events
- EVENT_WORKSTATION_LOCKED = 4800
- EVENT_SCREENSAVER_INVOKED = 4802
- EVENT_SHUTDOWN = 4609
- EVENT_LOGOFF = 4634
- EVENT_SESSION_DISCONNECTED = 4779
- EVENT_LOGOFF_INITIATED = 4647
