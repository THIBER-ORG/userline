#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

# App name
APP_NAME = 'UserLine'
# Version
VERSION = "0.2.3b"
# Log format
LOG_FORMAT = '%(levelname)s - %(message)s'

# Logon event types
LOGON_TYPE_INTERACTIVE = 2
LOGON_TYPE_NETWORK = 3
LOGON_TYPE_BATCH = 4
LOGON_TYPE_SERVICE = 5
LOGON_TYPE_UNLOCK = 7
LOGON_TYPE_NETWORKCLEAR = 8
LOGON_TYPE_NEWCREDS = 9
LOGON_TYPE_REMOTEINTERACTIVE = 10
LOGON_TYPE_CACHEDINTERACTIVE = 11
LOGON_TYPES = { \
			LOGON_TYPE_INTERACTIVE: 'Interactive (logon at keyboard and screen of system)', \
			LOGON_TYPE_NETWORK: 'Network (i.e. connection to shared folder on this computer from elsewhere on network)', \
			LOGON_TYPE_BATCH: 'Batch (i.e. scheduled task)', \
			LOGON_TYPE_SERVICE: 'Service (Service startup)', \
			LOGON_TYPE_UNLOCK: 'Unlock (i.e. unnattended workstation with password protected screen saver)', \
			LOGON_TYPE_NETWORKCLEAR: 'NetworkCleartext (Logon with credentials sent in the clear text. Most often indicates a logon to IIS with "basic authentication") See this article for more information.', \
			LOGON_TYPE_NEWCREDS: 'NewCredentials such as with RunAs or mapping a network drive with alternate credentials.  This logon type does not seem to show up in any events.  If you want to track users attempting to logon with alternate credentials see 4648.', \
			LOGON_TYPE_REMOTEINTERACTIVE: 'RemoteInteractive (Terminal Services, Remote Desktop or Remote Assistance)', \
			LOGON_TYPE_CACHEDINTERACTIVE: 'CachedInteractive (logon with cached domain credentials such as when logging on to a laptop when away from the network)', \
			}
# Local domain
LOCAL_DOMAIN = 'NT AUTHORITY'
CONSTANT_NA = 'N/A'

# Logoff events
EVENT_ACTION_LOGOFF = "Logoff"
EVENT_SHUTDOWN = 4609
EVENT_LOGOFF = 4634
EVENT_SESSION_DISCONNECTED = 4779
EVENT_LOGOFF_INITIATED = 4647
EVENTS_LOGOFF = [EVENT_SHUTDOWN,EVENT_LOGOFF,EVENT_SESSION_DISCONNECTED,EVENT_LOGOFF_INITIATED]
EVENT_WORKSTATION_LOCKED = 4800
EVENT_SCREENSAVER_INVOKED = 4802
EVENTS_LOGOFF_SCREEN = [EVENT_WORKSTATION_LOCKED,EVENT_SCREENSAVER_INVOKED]

# Logon events
EVENT_ACTION_LOGON = "Logon"
EVENT_LOGON = 4624
EVENT_LOGON_EXPLICIT = 4648
EVENT_SESSION_RECONNECTED = 4778
EVENTS_LOGON = [EVENT_LOGON,EVENT_LOGON_EXPLICIT,EVENT_SESSION_RECONNECTED]
EVENT_SCREENSAVER_DISMISSED = 4803
EVENT_WORKSTATION_UNLOCKED = 4801
EVENTS_LOGON_SCREEN = [EVENT_SCREENSAVER_DISMISSED,EVENT_WORKSTATION_UNLOCKED]

# Event descriptions
EVENT_DESCRIPTION = { \
		EVENT_WORKSTATION_LOCKED: 'Workstation locked' ,\
		EVENT_SCREENSAVER_INVOKED: 'Screensaver invoked' ,\
		EVENT_SHUTDOWN: 'Shutdown' ,\
		EVENT_LOGOFF: 'Logoff', \
		EVENT_SESSION_DISCONNECTED: 'Session disconnected' ,\
		EVENT_WORKSTATION_UNLOCKED: 'Workstation unlocked' ,\
		EVENT_SCREENSAVER_DISMISSED: 'Screensaver dismissed' ,\
		EVENT_LOGON: 'Logon' ,\
		EVENT_LOGON_EXPLICIT: 'Logon with explicit credentials' ,\
		EVENT_SESSION_RECONNECTED: 'RDP Session reconnected' \
		}

# Event actions (logon/logoff)
EVENT_ACTION = { \
		EVENT_WORKSTATION_LOCKED: EVENT_ACTION_LOGOFF ,\
		EVENT_SCREENSAVER_INVOKED: EVENT_ACTION_LOGOFF ,\
		EVENT_LOGOFF: EVENT_ACTION_LOGOFF ,\
		EVENT_SHUTDOWN: EVENT_ACTION_LOGOFF ,\
		EVENT_SESSION_DISCONNECTED: EVENT_ACTION_LOGOFF ,\
		EVENT_WORKSTATION_UNLOCKED: EVENT_ACTION_LOGON ,\
		EVENT_SCREENSAVER_DISMISSED: EVENT_ACTION_LOGON ,\
		EVENT_LOGON: EVENT_ACTION_LOGON ,\
		EVENT_LOGON_EXPLICIT: EVENT_ACTION_LOGON ,\
		EVENT_SESSION_RECONNECTED: EVENT_ACTION_LOGON \
		}

# Event skel (logon/logoff)
EVENT_SKEL = { \
		'index': CONSTANT_NA, \
		'type': CONSTANT_NA, \
		'eventid': CONSTANT_NA, \
		'description': CONSTANT_NA, \
		'username': CONSTANT_NA, \
		'domain': CONSTANT_NA, \
		'ipaddress': CONSTANT_NA, \
		'computer': CONSTANT_NA, \
		'srccomputer': CONSTANT_NA, \
		'datetime': CONSTANT_NA, \
		'timestamp': 0, \
		'logonid': CONSTANT_NA, \
		'sourceid': CONSTANT_NA, \
		'id': CONSTANT_NA,  \
		'srcid': CONSTANT_NA, \
		'raw': CONSTANT_NA \
	}

# Event struct (logon & logoff)
EVENT_STRUCT = { \
		# Logon data
		'duration': CONSTANT_NA, \
		'logon.datetime': CONSTANT_NA, \
		'logon.description': CONSTANT_NA, \
		'logon.username': CONSTANT_NA, \
		'logon.domain': CONSTANT_NA, \
		'logon.srcip': CONSTANT_NA, \
		'logon.srccomputer': CONSTANT_NA, \
		'logon.computer': CONSTANT_NA, \
		'logon.eventid': CONSTANT_NA, \
		'logon.type': CONSTANT_NA, \
		'logon.id': CONSTANT_NA, \
		'logon.sessionname': CONSTANT_NA, \
		'logon.srcid': CONSTANT_NA, \
		'logon.timestamp': 0, \
		# Logoff data
		'logoff.datetime': CONSTANT_NA, \
		'logoff.eventid': CONSTANT_NA, \
		'logoff.timestamp': 0, \
		# Metadata
		'logon.meta.id': CONSTANT_NA, \
		'logon.meta.uid': CONSTANT_NA, \
		'logon.meta.index': CONSTANT_NA,\
		'logoff.meta.id': CONSTANT_NA, \
		'logoff.meta.uid': CONSTANT_NA, \
		'logoff.meta.index': CONSTANT_NA, \
		# Logged on at a given time
		'mark.description': CONSTANT_NA, \
		'mark.value': CONSTANT_NA \
	}


# CSV fields
CSV_MARK_POS = [1,2]
CSV_FIELDS = [ \
		# Logon data
		'duration', \
		'mark.description', \
		'mark.value', \
		'logon.datetime', \
		'logon.description', \
		'logon.username', \
		'logon.domain', \
		'logon.srcip', \
		'logon.srccomputer', \
		'logon.computer', \
		'logon.eventid', \
		'logon.type', \
		'logon.id', \
		'logon.sessionname', \
		'logon.srcid', \
		'logon.timestamp', \
		# Logoff data
		'logoff.datetime', \
		'logoff.eventid', \
		'logoff.timestamp', \
		# Metadata
		'logon.meta.id', \
		'logon.meta.uid', \
		'logon.meta.index', \
		'logoff.meta.id', \
		'logoff.meta.uid', \
		'logoff.meta.index' \
	]
