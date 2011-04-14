'''
Distcraft message core module - manipulate XML messages from remote hosts

@author: James Ravenscroft
'''

import xml.parsers.expat
import xml.dom.minidom
import base64
import zlib

MIN_PROTOCOL_VERSION = 0.1

class MessageProtocolException(Exception):
    '''Exception thrown when a badly formed message is received.'''

    def __init__(self, version, message):
        Exception.__init__(self, " [DMP Version %f] %s" % (version, message) )


class MessageParser:
    '''The message parser reads XML messages from the remote host

    '''

    #---------------------GENERAL SAX PARSING PARAMS------------------------#
    '''The current status of the message Possible values are: * uninitialised
                         * transmitting
                         * finished
    '''
    messageStatus = "uninitialised"

    '''Get the name of the current element'''
    currentElement = None

    '''Instance of DistCore to send event information to'''
    broadcastCore = None

    '''A stack of names for the current element'''
    _inElement = []
    
    #----------------------------EVENT PARAMS-----------------------#
    
    '''Flag raised when an event is being parsed'''
    parsingEvent = False
    
    '''The name of the event being parsed'''
    eventName = ""
    
    '''A list of event arguments to be passed to the event handler'''
    eventArgs = []
    
    #--------------------ARG PARSING PARAMS-----------------------------#
    '''The type of the argument currently being parsed'''
    argType = None

    def __init__(self, core):
        ''' Create and set up the message parser
        '''

        #set up the xml parser stuff
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self._start_element
        self.parser.EndElementHandler = self._end_element
        self.parser.CharacterDataHandler = self._char_data

        #set up the broadcast core stuff
        self.broadcastCore = core

    def feed(self, chars):
        '''Send some characters to the XML parser'''
        self.parser.Parse(chars)

    def _start_element(self, name, attrs):
        '''Handle the beginning of a new XML element in the message
        '''

        #add this element to the stack
        if(self.currentElement != None):
            self._inElement.append(name)
        
        #get the current element name
        self.currentElement = name

        if(name == "message"):
            self.messageStatus = "transmitting"
            #make sure the protocol is compatible
            if( attrs['version'] < MIN_PROTOCOL_VERSION ):
                MessageProtocolException( attrs['version'], 
                "The client is using a version of the protocol that is too old.")
        
        if(name == "event"):
            if(self.parsingEvent == False):
                self.parsingEvent = True
            else:
                MessageProtocolException( attrs['version'], 
                "Malformed message: nested events not supported.")
                
            #get the name of the event
            if(attrs.has_key("name")):
                self.eventName = attrs['name']
            else:
                MessageProtocolException( attrs['version'], 
                "Malformed message: events must provide a name")
            
        if(name == "argument"):
            #if we are not inside an event, this shouldn't be here
            if(self.parsingEvent == False):
                MessageProtocolException( attrs['version'], 
                "Malformed message: argument must be part of an event.")
            else:
                #see what type of argument we have
                if(attrs.has_key("type")):
                    self.argType = attrs['type']
                else:
                    MessageProtocolException( attrs['version'], 
                    "Malformed message: Event arguments must provide a type")

    def _char_data(self, data):
        '''Handle character data from incoming messages'''
        
        if(self.currentElement == "argument"):
            if(self.argType == "int"):
                param = int(data)
            if(self.argType == "float"):
                param = float(data)
            if(self.argType == "string"):
                param = str(data)
                
            #add the parameter to the list for this event
            self.eventArgs.append(param)

    def _end_element(self, name):
        '''Handle the end of a new XML element in the message'''
        
        #pop the last element off the stack
        if( len(self._inElement) > 0):
            self.currentElement = self._inElement.pop()

        if(name == "message"):
            self.messageStatus = "finished"

        if(name == "event"):
            self.parsingEvent = False
            self._processEvent()

    def _processEvent(self):
        '''Process information gathered during an event parse'''
        args = self.eventArgs
        self.broadcastCore.fireEvent(self.eventName, *args)



class MessageBuilder:
    '''The message builder allows the generation of XML messages to be 
    sent to the remote host.

    '''

    def __init__(self):
        self.doc = xml.dom.minidom.Document()
        