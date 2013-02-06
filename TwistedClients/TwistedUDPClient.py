'''
Created on Jan 25, 2013

@author: jhollar
TwistedUDPClient.py

The purpose of this application is establish a locate an active service by first sending a UDP request to join
a subgroup. This application sends the following information to the subgroup requesting an active service TCP 
connection information:

        <client identifier>:<active service name>
            TwistedUDPClient:ActiveService01

If the service is available (active), the hub server returns the following information:
        <active service name>:<active service IP>:<active service PORT>
        
When received the client will establish a direct TCP connection using the service's IP and PORT information. 
This application will send a "Hello Service are you there?" message. The active service will return a response 
message "<service> Hello - Yes I'm here?".

When the application receives this message, it disconnects and stops

'''
from twisted.internet.protocol import DatagramProtocol, ClientFactory
from twisted.internet import reactor, protocol, defer
from twisted.python import log
import sys, signal, re

#global variables
ACTIVE_SERVER = "ActiveService01"

class ActiveServiceClientProtocol(protocol.Protocol):
    
    def connectionMade(self):
        log.msg("TwistedUDPClient connected to peer ")
        
    def dataReceived(self, data):  
        response = repr(data)
        
        # log.msg("TwistedUDPClient Received: %s" % response[0])   
        if ("<service>" in response):
            log.msg("received: %s" % repr(data))  
            self.transport.loseConnection()
        else: 
            self.transport.write("Hello Service are you there?")
        
    def sendData(self, data):
        connData = "TwistedUDPClient sent this %s" % repr(data)
        self.transport.write(connData)
       
    def connectionLost(self, why):
        log.msg("TwistedUDPClient: peer disconnected unexpectedly")
                             
class ActiveServiceClientFactory(ClientFactory):
    protocol = ActiveServiceClientProtocol()
    
    def __init__(self):
        self.deferred = defer.Deferred()
        
    def startedConnecting(self, connector):
        log.msg('ActiveServiceClientFactory Started to connect.')
        
    def buildProtocol(self, addr):
        log.msg('ActiveServiceClientFactory Connected.')
        return ActiveServiceClientProtocol()
        
    def clientConnectionFailed(self, connector, reason):
        log.msg("ActiveServiceClientFactory clientConnectionFailed %s" % reason)
        self.deferred.errback(reason)

    def clientConnectionLost(self, connector, reason):
        log.msg("ActiveServiceClientFactory clientConnectionLost %s" % reason)
        reactor.stop() #@UndefinedVariable
        # self.deferred.errback(reason)
        
class TwistedUDPClientService(DatagramProtocol):
    
    def stopProtocol(self):
        log.msg("Called after all transport is teared down")
        pass
    
    def datagramReceived(self, datagram, address):      
        received = re.sub('[\']', '', repr(datagram))
        response = received.split(":")
        active_service_name = response[0]
        active_service_ip = response[1]
        active_service_port = response[2]     
        try:
            active_service_port = int(active_service_port)
        except ValueError:
            active_service_port = 0
            log.err("ValueError thrown: ", "unknown")
        
        # log.msg("Received from TwistedHubServer: %s:%i" % (active_service_ip, active_service_port))
        
        if (active_service_port <=0):
            log.msg("TwistedHubServer: Service is not active")
            self.transport.loseConnection()
            reactor.stop() #@UndefinedVariable
        else:
            log.msg("TwistedUDPClient: %s - %s:%i" % (active_service_name, active_service_ip, active_service_port))
            connectToActiveService(active_service_name, "192.168.1.71", 8887)

def connectToActiveService(service, host, port):
    factory = ActiveServiceClientFactory()
    log.msg("Attempting to connect to Active Service %s - %s:%i" % (service, host, port))
    try:
        reactor.connectTCP(host, port, factory) #@UndefinedVariable
        response = factory.deferred()
        return response
    except Exception:
        log.msg("Failed to connect to Active Service %s - %s:%i" % (service, host, port))
                   
# signal handler to capture Ctl-C interrupts
def signal_handler(signal, frame):
        log.msg("You pressed Ctrl+C! - TwistedUDPClient was interrupted")
        reactor.stop() #@UndefinedVariable
    
#Initialization
log.startLogging(sys.stdout) 
signal.signal(signal.SIGINT, signal_handler)   
activeService = 'TwistedUDPClient:'+ACTIVE_SERVER
        
# Send multicast on 224.0.0.1:8888, on our dynamically allocated port
reactor.listenUDP(0, TwistedUDPClientService()).write(activeService, ('224.0.0.1', 8888)) #@UndefinedVariable
reactor.run() #@UndefinedVariable