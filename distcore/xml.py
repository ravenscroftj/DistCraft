import xml.parsers.expat



class MessageParser:
    '''The message parser reads XML messages from the remote host

    '''
    
    def __init__(self):
        ''''''
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self._start_element

    def _start_element(self, name, attrs):
        pass

    def _end_element(self, name):
        pass

class MessageBuilder:
    '''The message builder allows the generation of XML messages to be 
    sent to the remote host.

    '''