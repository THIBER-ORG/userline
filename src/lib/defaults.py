#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

from datetime import datetime,timedelta

ES_HOSTS="localhost"
ES_POOL_SIZE=5
NEO4J_BOLT="bolt://localhost:7678"
CSV_FILE="output.csv"
MIN_DATE=str(datetime.today() - timedelta(days=365)).split(' ')[0]
MAX_DATE=str(datetime.today()).split(' ')[0]

