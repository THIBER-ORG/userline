#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import re

re_time = re.compile(r'<TimeCreated +SystemTime="(.+)"/>')
re_logonid = re.compile(r'<Data +Name="(?:Target)?LogonId">(.+)</Data>')
re_logonsrcid = re.compile(r'<Data +Name="SubjectLogonId">(.+)</Data>')
re_tusername = re.compile(r'<Data +Name="(?:TargetUser|Account)Name">(.+)</Data>')
re_domain = re.compile(r'<Data +Name="(?:TargetDomainName|AccountDomain)">(.+)</Data>')
re_ipaddress = re.compile(r'<Data +Name="(?:IpAddress|ClientAddress)">(.+)</Data>')
re_srccomputer = re.compile(r'<Data +Name="ClientName">(.+)</Data>')
re_sessionname = re.compile(r'<Data +Name="SessionName">(.+)</Data>')
re_computer = re.compile(r'<Computer>(.+)</Computer>')
re_logontype = re.compile(r'<Data +Name="LogonType">(.+)</Data>')
