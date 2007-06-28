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
import cmd


sys.path.append('./')


from snmpquery import *

class Cli(cmd.Cmd):
	
	def emptyline(self):
		print "Type exit to terminate the session or type help."

	def default(self,line):
		print "*** Unknown Syntax : %s (type help for a list of valid command" % line

	def do_exit(self, arg):
		""" leave snmptools """		
		exit(0)

	def do_show_ifDescription(self,arg):
		""" Show the description of the networks interfaces 
			use : show_ifDescription
		"""
		try:
			mySnmpQuery=snmpQuery(self.ip,self.community)
		except AttributeError, error:
			print """WARNING: You must define a snmp agent before try to use !
	See snmpAgent command !"""
			return

		mySnmpQuery.list_ifDesc()

	def do_show_camTable(self, arg):
		""" Show the cam table of the agent
			use : show_camTable
		"""
		try:
			mySnmpQuery=snmpQuery(self.ip,self.community)
		except AttributeError, error:
			print """WARNING: You must define a snmp agent before try to use !
	See snmpAgent command !"""
			return
		mySnmpQuery.list_camTable()

	def do_show_macTable(self,arg):
		""" Show the mac table of the agent
			use : show_ifMac
		"""
		try:
			mySnmpQuery=snmpQuery(self.ip,self.community)
		except AttributeError, error:
			print """WARNING: You must define a snmp agent before try to use !
	See snmpAgent command !"""
			return
		mySnmpQuery.list_macTable()
		
	def do_show_operStatus(self,arg):
		""" Show the state of the networks interfaces 
			use : show_operStatus [verbose]
			[verbose]: UP and Down state
		"""
		try:
			mySnmpQuery=snmpQuery(self.ip,self.community)
		except AttributeError, error:
			print """WARNING: You must define a snmp agent before try to use !
	See snmpAgent command !"""
			return
		if (arg == "verbose"):
			mySnmpQuery.list_operStatus(True)
		else:
			mySnmpQuery.list_operStatus(False)
	
	def do_snmpAgent(self, arg):
		""" Configure a snmp agent
			use: snmpAgent [IP] [COMMUNITY]
			[IP]: ip address of the snmp v2c agent
			[COMMUNITY]: community of this agent
		"""
		champ=arg.split(' ')
		if (len(champ) == 2):
			self.ip = champ[0]
			self.community = champ[1]
		else:
			print """use: snmpAgent [IP] [COMMUNITY]
	[IP]: ip address of the snmp v2c agent
	[COMMUNITY]: community of this agent"""

	def do_print_agent(self,arg):
		""" Print snmp agent configured """
		try:
			print "SNMP agent ip address : %s" % self.ip
			print "SNMP agent community  : %s" % self.community
		except AttributeError, error:
			print """WARNING: You must define a snmp agent before try to use !
	See snmpAgent command !"""
			return

if (__name__=="__main__"):
	myCli = Cli()
	myCli.do_snmpAgent("194.167.159.254 imedias")
	myCli.prompt = "snmptools >"
	myCli.intro = """SNMP Tools (1.0) query command line interpreter.
		Type help or ? for help. """
	myCli.cmdloop()
