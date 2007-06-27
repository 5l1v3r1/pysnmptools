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

import re
import pysnmp
from pysnmp import role, v1, v2c, asn1

class GeneralException(Exception):
    "General exception"
    # Just subclass this with a new doc-string
    def __str__(self):
        # Returns a nice version of the docstring
        args = Exception.__str__(self) # Get our arguments
        result = self.__doc__
        if args:
            result += ": %s" % args
        return result

class SnmpError(GeneralException):
    """SNMP Error"""

class TimeOutException(SnmpError):
    """Timed out waiting for SNMP response"""

class NameResolverException(SnmpError):
    """NameResolverException"""

class NetworkError(SnmpError):
    """NetworkError"""

class AgentError(SnmpError):
    """SNMP agent responded with error"""

class EndOfMibViewError(AgentError):
    """SNMP request was outside the agent's MIB view"""

class UnsupportedSnmpVersionError(SnmpError):
    """Unsupported SNMP protocol version"""

class NoSuchObjectError(SnmpError):
    """SNMP agent did not know of this object"""


class Snmp:
	
	def __init__(self, host, community="public", version="2c", port=161, retries=3, timeout=1):
		self.host = host
		self.community = community
		self.version=version
		self.port=port
		self.retries=retries
		self.timeout=timeout
		
		self.handle=role.manager((host,port))

	def getValue(self, query):
		req=v2c.GETREQUEST()
		rsp=v2c.RESPONSE()
		req['encoded_oids'] = [ asn1.OBJECTID().encode(query) ]
		req['community'] = self.community
		(answer, src) = self.handle.send_and_receive(req.encode())
		rsp.decode(answer)
		if req != rsp:
		    raise 'Unmatched response: %s vs %s' % (str(req), str(rsp))

		oids = map(lambda x: x[0], map(asn1.OBJECTID().decode, rsp['encoded_oids']))
		vals = map(lambda x: x[0](), map(asn1.decode, rsp['encoded_vals']))

		if rsp['error_status']:
		    raise 'SNMP error #' + str(rsp['error_status']) + ' for OID #' \
		          + str(rsp['error_index'])
		#for (oid, val) in map(None, oids, vals):
		#    print oid + ' ---> ' + str(val)
		return vals[0]


	def _error_check(self, rsp):
        	"""Check a decoded response structure for agent errors or exceptions,
        	and raise Python exceptions accordingly."""
        
        	if rsp['error_status']:
            		error_index = rsp['error_index']-1
            		error_oid = asn1.decode(rsp['encoded_oids'][error_index])[0]
            		error_value = asn1.decode(rsp['encoded_oids'][error_index])[0]
            
            		if rsp['error_status'] == 2:
               			raise NoSuchObjectError(error_oid())
           		else:
               			raise AgentError("Error code %s at index %s (%s, %s)" % \
                                		(rsp['error_status'],
                                 		rsp['error_index'],
                                 		error_oid,
                                 		error_value))

        	rsp_oids = [asn1.decode(o)[0] for o in rsp['encoded_oids']]
        	rsp_values = [asn1.decode(v)[0] for v in rsp['encoded_vals']]

        	for rsp_oid, rsp_value in zip(rsp_oids, rsp_values):
            		if isinstance(rsp_value, (asn1.noSuchObject, asn1.noSuchInstance)):
                		raise NoSuchObjectError(rsp_oid)
            		elif isinstance(rsp_value, asn1.endOfMibView):
                		raise EndOfMibViewError(rsp_oid())


	def walk(self,query=".1.3.6.1.2.1.2.2.1.2"):
		"""
		Methode pour parcourir la MIB.
		"""
		if not query.startswith("."):
			query = "." + query
		snmp = self.version
		result=[]
		monOid=asn1.OBJECTID()
		monOid.encode(query)
		
		req = v2c.GETNEXTREQUEST()
		req['community'] = self.community
		req['encoded_oids'] = [monOid.encode()]
		
		rsp = v2c.RESPONSE()
		current_oid = monOid

		while 1:
						
			try:
				(answer, src) = self.handle.send_and_receive(req.encode())
			except role.NoResponse, e:
				raise TimeOutException(e)
			except role.NetworkError, n:
				raise NetworkError(n)
			
			rsp.decode(answer)
			try:
				self._error_check(rsp)
			except EndOfMibViewError:
				return result
			rsp_oid = asn1.decode(rsp['encoded_oids'][0])[0]
			rsp_value = asn1.decode(rsp['encoded_vals'][0])[0]
			if not monOid.isaprefix(rsp_oid()):
				return result
			elif rsp_oid == current_oid:
				return result
			else:
				result.append((rsp_oid(), str(rsp_value())))
				
			req['request_id'] += 1
			req['encoded_oids'] = rsp['encoded_oids']
			current_oid = rsp_oid
