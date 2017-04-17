#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

# App name
APP_NAME = 'UserLine'
# Version
VERSION = "0.2.1b"
# Log format
LOG_FORMAT = '%(levelname)s - %(message)s'

# Logon event types
LOGON_TYPES = { \
			2: 'Interactive (logon at keyboard and screen of system)', \
			3: 'Network (i.e. connection to shared folder on this computer from elsewhere on network)', \
			4: 'Batch (i.e. scheduled task)', \
			5: 'Service (Service startup)', \
			7: 'Unlock (i.e. unnattended workstation with password protected screen saver)', \
			8: 'NetworkCleartext (Logon with credentials sent in the clear text. Most often indicates a logon to IIS with "basic authentication") See this article for more information.', \
			9: 'NewCredentials such as with RunAs or mapping a network drive with alternate credentials.  This logon type does not seem to show up in any events.  If you want to track users attempting to logon with alternate credentials see 4648.', \
			10: 'RemoteInteractive (Terminal Services, Remote Desktop or Remote Assistance)', \
			11: 'CachedInteractive (logon with cached domain credentials such as when logging on to a laptop when away from the network)', \
			}
# Local domain
LOCAL_DOMAIN = 'NT AUTHORITY'

# Logoff events
EVENT_ACTION_LOGOFF = "Logoff"
EVENT_WORKSTATION_LOCKED = 4800
EVENT_SCREENSAVER_INVOKED = 4802
EVENT_SHUTDOWN = 4609
EVENT_LOGOFF = 4634
EVENT_SESSION_DISCONNECTED = 4779
EVENTS_LOGOFF = [EVENT_WORKSTATION_LOCKED,EVENT_SCREENSAVER_INVOKED,EVENT_SHUTDOWN,EVENT_LOGOFF,EVENT_SESSION_DISCONNECTED]

# Logon events
EVENT_ACTION_LOGON = "Logon"
EVENT_WORKSTATION_UNLOCKED = 4801
EVENT_SCREENSAVER_DISMISSED = 4803
EVENT_LOGON = 4624
EVENT_LOGON_EXPLICIT = 4648
EVENT_SESSION_RECONNECTED = 4778
EVENTS_LOGON = [EVENT_WORKSTATION_UNLOCKED,EVENT_SCREENSAVER_DISMISSED,EVENT_LOGON,EVENT_LOGON_EXPLICIT,EVENT_SESSION_RECONNECTED]

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
		EVENT_SESSION_RECONNECTED: 'Session reconnected' \
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
		'type': '', \
		'eventid': '', \
		'description': '', \
		'username': '', \
		'domain': '', \
		'ipaddress': '', \
		'computer': '', \
		'datetime': '', \
		'timestamp': 0, \
		'logonid': '', \
		'sourceid': '', \
		'id': '',  \
		'srcid': '', \
		'raw': '' \
	}

# Event struct (logon & logoff)
EVENT_STRUCT = { \
		# Logon data
		'duration': 'N/A', \
		'logon.datetime': 'N/A', \
		'logon.description': 'N/A', \
		'logon.username': 'N/A', \
		'logon.domain': 'N/A', \
		'logon.srcip': 'N/A', \
		'logon.computer': 'N/A', \
		'logon.eventid': 'N/A', \
		'logon.type': 'N/A', \
		'logon.id': 'N/A', \
		'logon.srcid': 'N/A', \
		'logon.timestamp': 0, \
		# Logoff data
		'logoff.datetime': 'N/A', \
		'logoff.description': 'N/A', \
		'logoff.username': 'N/A', \
		'logoff.domain': 'N/A', \
		'logoff.computer': 'N/A', \
		'logoff.eventid': 'N/A', \
		'logoff.type': 'N/A', \
		'logoff.id': 'N/A', \
		'logoff.timestamp': 0, \
		# Metadata
		'logon.meta.id': 'N/A', \
		'logon.meta.uid': 'N/A', \
		'logoff.meta.id': 'N/A', \
		'logoff.meta.uid': 'N/A', \
		# Logged on at a given time
		'mark.description': 'N/A', \
		'mark.value': 'N/A' \
	}


# CSV fields
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
		'logon.computer', \
		'logon.eventid', \
		'logon.type', \
		'logon.id', \
		'logon.srcid', \
		'logon.timestamp', \
		# Logoff data
		'logoff.datetime', \
		'logoff.description', \
		'logoff.username', \
		'logoff.domain', \
		'logoff.computer', \
		'logoff.eventid', \
		'logoff.type', \
		'logoff.id', \
		'logoff.timestamp', \
		# Metadata
		'logon.meta.id', \
		'logon.meta.uid', \
		'logoff.meta.id', \
		'logoff.meta.uid' \
	]
