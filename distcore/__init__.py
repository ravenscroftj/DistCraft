'''
The Distcraft core module contains all basic core definitions for the engine
including communications modules and parsers. Non-essential, customisable parts
of the program such as physics and graphics engines are 'plugins' and are not
part of the core

@author: James Ravenscroft
'''
import sys
import socket
import asyncore
import threading

#import distcore messenging service
import messages

class EventHandlerException(Exception):
    '''Exception thrown when the event handler has problems'''
    def __init__(self, message,eventname):
        Exception.__init__("Error while handling event '%s', %s" % 
                                                    (message,eventname))
        

#--------------------------------------------------------------------------#

class DistCore(asyncore.dispatcher):
    
    __doc__= '''
    The DistCore class creates a listening server that is able to detect other 
    distcore requests and handle them
    '''
    __running = False
    
    '''Create an empty dict ready for event handlers. These are registered
    with the core and fired by subprocesses'''
    _evt_handlers = {}
    
    '''Flag raised when debug mode is enabled at the commandline'''
    debug = False
    
    '''Flag raised when verbose mode is enabled at commandline'''
    verbose = False
    
    '''Mutex that locks core operations to a single thread'''
    _cLock = None
    
    '''A list of connected clients'''
    _clients = []
    
    def __init__(self):
        #set up async stuff
        asyncore.dispatcher.__init__(self)
        
        #set up the core lock
        self._cLock = threading.Lock()

        #register internal core events
        self.register_event_handler("distcraft.server.new_client", 
                                        self._onAcceptClient)
                                        
        self.register_event_handler("client.disconnect", self._onClientDisconnect)
                                        
        #register as handler for client greeting message
        #self.register_event_handler("client.greeting", self._onClientGreeting)
                                        
    def __del__(self):
        #self.insock.close()
        pass
        
    def serve(self, port):
        '''Bind to a local socket and listen for incoming requests from users'''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()        
        self.bind( ('localhost', port) )
        
        #listen for incoming connections
        self.listen(5)
        
        self.log( "INFO" , "Listening on port " + str(port))
    
        #loop asyncore
        asyncore.loop()
            
    def handle_accept(self):
        '''Async stuff for binding to the local socket'''
        newsock, address = self.accept()

        self.fireEvent("distcraft.server.new_client", self, newsock, address)
            
    def register_event_handler(self, event, callback_function):
        '''Add an event handler with named callback function to the core'''
        #lock the object
        self._cLock.acquire()
        #add the new event handler
        self._evt_handlers[event] = callback_function
        #release the lock
        self._cLock.release()
        
    def unregister_event_handler(self, event):
        '''Remove a registered event handler from the core'''
        #lock the object
        self._cLock.acquire()
        self._evt_handlers.pop(event)
        #release the lock
        self._cLock.release()
        
    def fireEvent(self, event, source, *args):
        '''Fires an event for the given event name or causes an error'''
        #lock the object
        self._cLock.acquire()
        if(self._evt_handlers.has_key(event)):
            self._evt_handlers[event](source, *args)
        else:
            self.log("ERROR", "No event handler registered for %s" % event)
        #release the lock
        self._cLock.release()
        
    def log(self, level, message):
        '''
        Log an event or a problem in the core
        '''
        if((level == "DEBUG") & (self.debug == False)):
            return
        
        if((level == "NOTICE") & (self.verbose == False)):
            return
        
        print "[ %s ] %s" % (level,message)
        
        
    def _onClientDisconnect(self, client):
        '''Event handler triggered when a client disconnects from the socket'''
        self._clients.remove(client)
        client.kill()

    def _onAcceptClient(self, eventsource, clientsocket, clientaddress):
        '''Accept an incoming connection from a client 
        '''
        self.log( "INFO" , "New client has connected from " + str(clientaddress))
        
        client = ClientHandler(clientsocket, self)
        client.greet()
        self._clients.append( client )
        
    def connect(self, address, port):
        client = ClientCore( self, address, port)
        
        
        #add the client to the list of clients
        self.clients.append(client)

#---------------------------------------------------------------------------#
        
class ClientHandler(asyncore.dispatcher_with_send):
    
    def __init__(self, socket, core):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self.core = core
        self.mparser = messages.MessageParser(core, self)
        
        self.mbuilder = messages.MessageBuilder()
        self.mbuilder
        
    def greet(self):
        '''Once a connection with the client has been made, greet them'''
        self.mbuilder.addEvent("client.greeting")
        self.out_buffer = self.mbuilder.getMessage()
        
    def kill(self):
        self.mbuilder.addEvent("server.disconnect")
        self.out_buffer = self.mbuilder.getMessage()
        self.close()
        
        
    def send_error(self, text):
        self.mbuilder.addEvent("client.protocol.error", text)
        self.out_buffer = self.mbuilder.getMessage()
        
    def handle_read(self):
        
        if(self.mparser.messageStatus == "finished"):
            self.mparser.resetParser()
            
        try:
            self.mparser.feed(self.recv(8192))
        except messages.MessageProtocolException as e:
            self.send_error(e.message)
            self.core.log("ERROR", "Error '%s' from client " % (e.message))
            
#---------------------------------------------------------------------------#
            