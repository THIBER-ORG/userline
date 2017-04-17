#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/sch3m4/userline
#

import re

re_time = re.compile(r'<TimeCreated +SystemTime="(.+)"/>')
re_logonid = re.compile(r'<Data +Name="TargetLogonId">(.+)</Data>')
re_logonsrcid = re.compile(r'<Data +Name="SubjectLogonId">(.+)</Data>')
re_tusername = re.compile(r'<Data +Name="TargetUserName">(.+)</Data>')
re_domain = re.compile(r'<Data +Name="TargetDomainName">(.+)</Data>')
re_ipaddress = re.compile(r'<Data +Name="IpAddress">(.+)</Data>')
re_computer = re.compile(r'<Computer>(.+)</Computer>')
re_logontype = re.compile(r'<Data +Name="LogonType">(.+)</Data>')
