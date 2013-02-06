'''
Created on Jan 25, 2013

@author: jhollar
TwistedHubServer.py

The purpose of this module is to provide a simple identification and lookup mechanism for client 
applications wishing to obtain network access to a specific active services. 

This module uses a pre-defined UDP multicast group to listen for requests from either a client or active service
who wish to establish a TCP connection. This is the "master" controller and must be active receiving UDP packets. 

When this module receives an active service activation request, the service name and network information are persisted in a dictionary.
When this module receives an active service shutdown request, the service name is removed from the persisted dictionary.

When this module receives a client request for an active service, the service name given is used to lookup the service in a 
persisted dictionary maintained by this service. If found the IP address of that service is returned to the client requesting the service. 

Note: for this simple solution, there's an implied assumption that all "active services" will be listing on port 8887.

Once a client receives the "active" service's IP address, the client will communicate directly with the "active"
service by establishing a TCP connection. 

'''
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, protocol
from twisted.python import log
from Persistence import Persistent
import re
import sys

#global variables
DEFAULT_ASPORT = 8887
AS_PORT = 0
ACTIVE_SERVICES = {}

class TwistedHubForwardingProtocol(protocol.Protocol):
    def __init__(self):
        self.output = None
        self.normalizeNewlines = False
        
    def dataReceived(self, data):
        if self.normalizeNewlines:
            data = re.sub(r"(\r\n|\n)", "\r\n", data)
        if self.output:
            self.output.write(data)
    
class TwistedHubService(DatagramProtocol):
    def startProtocol(self):
        log.msg('Started Listening - 224.0.0.1:8888')
        # Join a specific multicast group, which is the IP we will respond to
        self.transport.joinGroup('224.0.0.1')

    def datagramReceived(self, datagram, address):
        global AS_PORT
        global ACTIVE_SERVICES
        global DEFAULT_ASPORT
        
        response = datagram.split(":") 
        
        # The uniqueID check is to ensure we only service requests from ourselves
        if response[0] == 'TwistedUDPClient':   
                   
            # Obtain the active server information based on the second parameter 
            # which should be the active server key value
            active_server = re.sub('[\']', '', repr(response[1])).strip()
            
            try:
                # ASstring will contain <ip address>:<port number>
                ASstring = ACTIVE_SERVICES[active_server]
                asIP = re.sub('[\']', '', repr(ASstring[0])).strip()
                asPORT = re.sub('[\']', '', repr(ASstring[1])).strip()
                ACTIVE_SERVICES.sync()
                
                # Send it back to the caller 
                self.transport.write(active_server + ":"+ asIP +":"+ asPORT, address)
                log.msg("information sent to client - Active Service %s is at %s:%s" % (active_server, asIP, asPORT))
            except Exception:
                self.transport.write('Active Service Exception: '+ active_server + " null:null", address)
                log.msg("information sent to client - Active Service %s is not active" % active_server)
                   
        if response[0] == 'TwistedHubService': 
                     
            """
            When the datagram receives a TwistedHubService message, that message contains the following:
                 service name, service IP address and service PORT number. 
                
                The format of the message will be:
            
                TwistedHubService:<ActiveServiceName>:<active_service_ip>:<active_service_port>
                ex:    TwistedHubService:ActiveService01:192.168.164.71:8887
                
            """           
            active_server = re.sub('[\']', '', repr(response[1])).strip()
            asIP = re.sub('[\']', '', repr(response[2])).strip()
            asPORT = re.sub('[\']', '', repr(response[3])).strip()
            
            """
             TODO: Need to add better validation of message content here!
            
            log.msg("Active Service Identified as (%s) %s:%s" % (active_server, asIP, asPORT))
            """
            
            """
            An active service is identified by it's service name. Each service name must be
            unique because it will be used as the key to locate the service's IP and PORT number.
            The value associated with each service name will be a string value formatted as:
            
                    <service IP address>:<service PORT number>
                    ex.    192.168.164.71:8887
            """
            ACTIVE_SERVICES[active_server] = asIP + ":" + asPORT
            ACTIVE_SERVICES.sync()          # Make sure we save the service information to disk.
            
            """
            At this point we are going to send the original message back to the caller.
            """           
            self.transport.write('from TwistedHubService ', address)
            
        if response[0] == 'TwistedHubServiceRemove': 
            """
            When the datagram receives a TwistedHubServiceRemove message, that message will contain the 
            service name, service IP address and service PORT number. The format of the message will be:
            
                TwistedHubServiceRemove:<ActiveServiceName>:<active_service_ip>:<active_service_port>
                ex:    TwistedHubService:ActiveService01:192.168.164.71:8887
                
            When this message is received, the active service component is requesting that it be removed
            as being "active". 
            """                       
            active_server = re.sub('[\']', '', repr(response[1])).strip()
            asIP = re.sub('[\']', '', repr(response[2])).strip()
            asPORT = re.sub('[\']', '', repr(response[3])).strip()
            
            log.msg("ActiveService removed from hub (%s) %s:%s" % (active_server, asIP, asPORT))
            
            del(ACTIVE_SERVICES[active_server])
            ACTIVE_SERVICES.sync()

            # Send it back to the caller 
            self.transport.write('from TwistedHubService service has been removed ', address)
            
log.startLogging(sys.stdout)    
# Make and use a persistent dictionary
ACTIVE_SERVICES = Persistent.PersistentDict('activeservices.json', 'c', format='json')  
             
# Listen for multicast on 224.0.0.1:8888
reactor.listenMulticast(8888, TwistedHubService()) #@UndefinedVariable
reactor.run() #@UndefinedVariable
ACTIVE_SERVICES.close()