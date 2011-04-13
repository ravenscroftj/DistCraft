import socket


class DistCore:
    
    __doc__= '''
    The DistCore class creates a listening server that is able to detect other 
    distcore requests and handle them
    '''
    running = False
    
    '''Create an empty dict ready for event handlers. These are registered
    with the core and fired by subprocesses'''
    evt_handlers = {}
    
    def __init__(self):
        #build an incoming socket for clients to join up with
        self.insock = socket.socket()
        pass
        
        
    def listen(self, port):
        self.insock.bind( ("127.0.0.1", port))
        
        #wait for some incoming connections
        running = True
        
        while(running == True):
            newsock, address = self.insock.accept()
            
    def register_event_handler(self, event, callback_function):
        '''Add an event handler with named callback function to the core'''
        self.evt_handlers[event] = callback_function
        
    def unregister_event_handler(self, event):
        '''Remove a registered event handler from the core'''
        self.evt_handlers.pop(event)
        