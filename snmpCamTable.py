import sys

sys.path.append('./')
from snmpquery import *


if (len(sys.argv)>1):
 mySnmpQuery=snmpQuery(sys.argv[1],sys.argv[2])
 mySnmpQuery.list_camTable()
else:
 print sys.argv[0]+" [IP ADDRESS] [COMMUNITY]"
