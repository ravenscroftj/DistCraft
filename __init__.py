'''Welcome to Distcraft - a distributed game server library

Distcraft aims to provide a platform that can be used to set up distributed 
online games.
'''

import sys
import optparse


from core import DistCore

DEFAULT_PORT = 1221

if __name__ == "__main__":
    
    d = DistCore()
    
    if(len(sys.argv) > 1):
        #get the options
        o   = optparse.OptionParser()
        o.add_option("-v", "--verbose", action="store_true", dest="verbose")
        o.add_option("-d", "--debug", action="store_true", dest="debug")
        o.add_option("-p", "--port" , action="store", dest="port", default=DEFAULT_PORT)
        
    else:
        d.listen(DEFAULT_PORT)