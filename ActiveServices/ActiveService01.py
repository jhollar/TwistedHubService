'''
Created on Jan 25, 2013

@author: jhollar
ActiveService01.py

This module represents an active service which provide an Internet-enabled service which 
identifies itself as being available for receiving and processing messages across a TCP connection

This is a basic example which uses listens for TCP connections from a client process on port 8887.

'''
from twisted.internet import reactor, protocol
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log
import sys, signal, re, socket

#global variables
SERVERNAME = "ActiveService01"
PORT = 0
IP = ""

# Multi-cast Variables
UDPGROUP = '224.0.0.1'
UDPPORT = 8888

class ActiveServiceProtocol(protocol.Protocol):
    def startProtocol(self):
        log.msg("Active Service is Listening - %s:%d" % (self.transport.host, PORT))
        
    def dataReceived(self, data):
        log.msg("Received: %s" % repr(data))
        # For now, just echo what was received back to the caller
        self.t.write("<service> Hello - Yes I'm here?")
        
    def makeConnection(self, transport):
        self.t = transport
        connData = "%s:%d" % (IP, PORT)
        self.t.write(connData)
        log.msg("Active Service %s available - %s:%d" % (SERVERNAME, IP, PORT))
        
    def sendData(self, data):
        #log.msg("Client sent this %s" % repr(data))
        self.t.write("Hello")

class ActiveServiceServerFactory(protocol.ServerFactory):
    protocol = ActiveServiceProtocol
    
    def connectionMade(self):
        log.msg("Started Listening - %s:%d" % (self.transport.host, PORT))
       
    def serverConnectionLost(self, connector, reason):
        log.msg("Lost connection: %s" % reason.getErrorMessage())
        reactor.stop() #@UndefinedVariable
        
    def serverConnectionFailed(self, connector, reason):
        log.msg("Connection failed: %s " % reason.getErrorMessage())
        
class TwistedHubServerService(DatagramProtocol):
                   
    def stopProtocol(self):
        log.msg("Called after all transport is torn down")
        pass

    def datagramReceived(self, datagram, address):
        response = re.sub('[\']', '', repr(address)).split(",")
        active_server_ip = re.sub('[(]', '', response[0]).strip()
        active_server_port = re.sub('[)]', '', response[1]).strip()   
        log.msg("Received from TwistedHubServer: %s:%s" % (active_server_ip, active_server_port))
 
# This is a bit of a hack but I've tested it on "nix", Windows and MacOS and it works.
def initializeServiceIdentity():
    global IP
    global PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80)) 
    IP = s.getsockname()[0]
    PORT = 8887
    s.close()
    
# signal handler to capture Ctl-C interrupts
def signal_handler(signal, frame):
        log.msg("You pressed Ctrl+C!")
        activeService = 'TwistedHubServiceRemove:'+SERVERNAME+":"+ re.sub('[\']', '', repr(IP)).strip() +":"+ re.sub('[\']', '', repr(PORT)) 
        reactor.listenUDP(0, TwistedHubServerService()).write(activeService, (UDPGROUP, UDPPORT)) #@UndefinedVariable
        reactor.stop() #@UndefinedVariable
           
# Initialize 
log.startLogging(sys.stdout)
signal.signal(signal.SIGINT, signal_handler)

# Make sure we initialize our service identification to obtain the local IP address and port number
initializeServiceIdentity()

activeService = 'TwistedHubService:'+SERVERNAME+":"+ re.sub('[\']', '', repr(IP)).strip() +":"+ re.sub('[\']', '', repr(PORT)) 
  
reactor.listenTCP(PORT, ActiveServiceServerFactory()) #@UndefinedVariable

log.msg("%s UDP multicasting on %s:%d" % (SERVERNAME, UDPGROUP, UDPPORT))
reactor.listenUDP(0, TwistedHubServerService()).write(activeService, (UDPGROUP, UDPPORT)) #@UndefinedVariable
reactor.run() #@UndefinedVariable