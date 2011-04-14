'''
The Distcraft core module contains all basic core definitions for the engine
including communications modules and parsers. Non-essential, customisable parts
of the program such as physics and graphics engines are 'plugins' and are not
part of the core

@author: James Ravenscroft
'''

import socket
import threading

#import distcore messenging service
import messages

class EventHandlerException(Exception):
    '''Exception thrown when the event handler has problems'''
    def __init__(self, message,eventname):
        Exception.__init__("Error while handling event '%s', %s" % 
                                                    (message,eventname))
        

#--------------------------------------------------------------------------#

class DistCore(object):
    
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
    
    def __init__(self):
        
        #set up the core lock
        self._cLock = threading.Lock()
        #build an incoming socket for clients to join up with
        self.insock = socket.socket()
        
        #register internal core events
        self.register_event_handler("distcraft.server.new_client", 
                                        self._onAcceptClient)
                                        
    def __del__(self):
        self.insock.close()
        
    def listen(self, port):
        '''Bind to a local socket and listen for incoming requests from users'''
        self.insock.bind( ('127.0.0.1', port) )
        
        self.log( "INFO" , "Listening on port " + str(port))
        
        #listen for incoming connections
        self.insock.listen(5)
        
        #wait for some incoming connections
        self.__running = True
        
        while(self.__running == True):
            newsock, address = self.insock.accept()
            self.fireEvent("distcraft.server.new_client", newsock, address)
            
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
        
    def fireEvent(self, event, *args):
        '''Fires an event for the given event name or causes an error'''
        #lock the object
        self._cLock.acquire()
        if(self._evt_handlers.has_key(event)):
            self._evt_handlers[event](*args)
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
        

    def _onAcceptClient(self, clientsocket, clientaddress):
        '''Accept an incoming connection from a client '''
        c = CoreListenWorker(self, clientsocket, clientaddress)
        c.start()
        

#---------------------------------------------------------------------------#
        
class CoreListenWorker(threading.Thread):
    '''This class is used to handle incoming client requests'''
    
    def __init__(self, core, clientsocket, clientaddress):
        #initialse thread around this class
        threading.Thread.__init__(self)
        #get the core information
        self.core = core
        #store client socket and address
        self.socket = clientsocket
        self.addr = clientaddress
        
    def run(self):
        '''Thread allows the worker to run and talk to the client'''
        
        #to start with, the client is definitely connected
        running = True
        
        #send the user hello message and wait for a response
        m = messages.MessageBuilder()
        m.addEvent("client.greeting")
        
        #Send the message to the user
        self.socket.send(m.getMessage())
        
#---------------------------------------------------------------------------#

class ClientCore(object):
    ''' The client core is responsible for connecting to other nodes and 
    talking to them on request.
    '''
    def __init__(self, core):
        '''Generate a new client to talk to other distcraft nodes'''
        self.outsock = socket.socket()
        
    def connect(self, server, port):
        '''Connect to a remote client and talk to them'''
        self.outsock.connect((server,port))
