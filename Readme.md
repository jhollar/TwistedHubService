# Overview

I created this project for two reasons; first I wanted to create a simple service discovery solution that allows the discovery of 
one or more active software service components. The goal was to provide a central point of interconnection for diverse 
Internet-enabled services without the need for special static configurations. 

An active service component is defined as any Internet-enabled service which identifies itself as being available for receiving 
and processing messages across a TCP connection. The feature set provided by an active service component is not relevant here 
because I wanted to provide a common way of service discovery. The second reason for creating this project was that I needed an 
excuse to learn Twisted Python. 

I hope this code is helpful to others as a foundation for using twisted as the basis for active service discovery. 

[Find me on LinkedIn](www.linkedin.com/pub/jeff-hollar/0/6b7/813/)

# System Overview

This system is composed of the following:

TwistedHubServer
----------------
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

ActiveService01
---------------
This module represents an active service which provide an Internet-enabled service which 
identifies itself as being available for receiving and processing messages across a TCP connection

This is a basic example which uses listens for TCP connections from a client process on port 8887.

TwistedUDPClient
----------------
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

# Installing and using Eclipse

I used the Eclipse PyDev plug-in to develop this project. There was a great article on stackoverflow describing how to run twisted 
python application in PyDev [Running a Twisted Application in PyDev](http://stackoverflow.com/questions/4794707/running-a-twisted-application-in-pydev)

When you have Eclipse setup, you run all three applications from within Eclipse.

# Running from the command line

The following illustrates how the components interact and how I tested their logic: 




# License

Apache License: http://www.apache.org/licenses/LICENSE-2.0.html

# Future Enhancements
This is a very basis system which could be extended to provide more robust production quality features. Here are a few items I can think of 
which might be nice to have:


