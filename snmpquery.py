# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys
import time
import threading

sys.path.append('./')
from snmp import *

class convertValue:
	def hexToString(self, octets):
		return ":".join( [ '%x'%(ord(c)) for c in octets ] )

class snmpQueryGetBandWidth(threading.Thread):
	def __init__(self, host, community, interface):
		threading.Thread.__init__(self)
		self.client = Snmp(host,community)
		self.monTimer = 1
		self.iface = interface
		self.Terminated=False

	def get_bandWidth(self):
		ifSpeed = self.client.getValue(".1.3.6.1.2.1.2.2.1.5."+self.iface)
		DeltaIfIn1 = self.client.getValue(".1.3.6.1.2.1.2.2.1.10."+self.iface)
		time.sleep(self.monTimer)
		DeltaIfIn2 = self.client.getValue(".1.3.6.1.2.1.2.2.1.10."+self.iface)
		InputUtilization = ((DeltaIfIn2-DeltaIfIn1)*8*100)/(self.monTimer*ifSpeed*1.0)
		print "Interface",self.iface," Input:", InputUtilization
		return


	def run(self):
		i = 0
		while not self.Terminated:
			self.get_bandWidth()
			time.sleep(self.monTimer)
		return

	def stop(self):
		self.Terminated=True
		return


class snmpQuery:
	def __init__(self, host, community):
		self.client = Snmp(host,community)
	
	def list_camTable(self):
		result=[]
		subTab = self.client.walk(".1.3.6.1.2.1.17.4.3.1.1")
		for valeur in subTab:
			field = valeur[0].split('.')
			nbElt = len(field)
			bridge=field[nbElt-6]+"."+field[nbElt-5]+"."+field[nbElt-4]+"."+field[nbElt-3]+"."+field[nbElt-2]+"."+field[nbElt-1]
			result.append((self.client.getValue(".1.3.6.1.2.1.17.4.3.1.2."+bridge),valeur[1]))
		for elt in result:
			print "INSERT INTO camtable VALUES('','%s','%s','%s','%s');"%(self.client.host,self.client.getValue(".1.3.6.1.2.1.31.1.1.1.1."+str(elt[0])),convertValue().hexToString(elt[1]),time.strftime("%H:%M:%S %d/%m/%Y", time.localtime()))

	def list_macTable(self):
		result=[]
		subTab = self.client.walk(".1.3.6.1.2.1.4.22.1.2")
		for valeur in subTab:
			field = valeur[0].split('.')
			nbElt = len(field)
			result.append((field[nbElt-5],field[nbElt-4]+"."+field[nbElt-3]+"."+field[nbElt-2]+"."+field[nbElt-1],valeur[1]))
		for elt in result:
			print "%s: \t\t%s (%s)"%(self.client.getValue(".1.3.6.1.2.1.2.2.1.2."+elt[0]),convertValue().hexToString(elt[2]),elt[1])

	def list_ifDesc(self):
		result = self.client.walk(".1.3.6.1.2.1.2.2.1.2")
		for valeur in result:
			print valeur[1]
	
	def list_operStatus(self, verbose=False):
		result = self.client.walk(".1.3.6.1.2.1.2.2.1.2")
		for valeur in result:
			indexIf=valeur[0].split('.')
			operStatus=self.client.getValue(".1.3.6.1.2.1.2.2.1.8."+indexIf[-1])
			if (operStatus == 1):	
				operStatus = "UP"
			elif (operStatus != 1):
				operStatus = "DOWN"
			if (not verbose and operStatus == "UP"):
				print "%s \t-> %s" % (str(valeur[1]),operStatus)
			elif (verbose):
				print "%s \t-> %s" % (str(valeur[1]),operStatus)

