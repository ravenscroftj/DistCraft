'''
Distcraft message core module - manipulate XML messages from remote hosts

@author: James Ravenscroft
'''

import xml.parsers.expat
import xml.dom.minidom


class MessageParser:
    '''The message parser reads XML messages from the remote host

    '''

    '''The current status of the message

    Possible values are: * uninitialised
                         * transmitting
                         * finished
    
    '''
    messageStatus = "uninitialised"

    '''Get the name of the current element'''
    currentElement = None

    broadcastCore = None

    '''A stack of names for the current element'''
    _inElement = []

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

    def _char_data(self, data):
        '''Handle character data from incoming messages'''

    def _start_element(self, name, attrs):
        '''Handle the beginning of a new XML element in the message'''

        #add this element to the stack
        if(self.currentElement != None):
            self._inElement.append(name)
        
        #get the current element name
        self.currentElement = name

        if(name == "message"):
            self.messageStatus = "transmitting"

    def feed(self, chars):
        '''Send some characters to the XML parser'''
        self.parser.Parse(chars)

    def _end_element(self, name):
        '''Handle the end of a new XML element in the message'''
        
        #pop the last element off the stack
        if( len(self._inElement) > 0):
            self.currentElement = self._inElement.pop()

        if(name == "message"):
            self.messageStatus = "finished"


class MessageBuilder:
    '''The message builder allows the generation of XML messages to be 
    sent to the remote host.

    '''

    def __init__(self):
    