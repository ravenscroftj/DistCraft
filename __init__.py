'''Welcome to Distcraft - a distributed game server library

Distcraft aims to provide a platform that can be used to set up distributed 
online games.
'''

import sys
import optparse

from distcore import DistCore

DEFAULT_PORT = 1221

def main():    
    d = DistCore()
    
    #get the options
    o   = optparse.OptionParser()
    o.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    o.add_option("-d", "--debug", action="store_true", dest="debug", default = False)
    o.add_option("-p", "--port" , action="store", dest="port", default=DEFAULT_PORT)
    
    opts, args = o.parse_args()
    
    if(opts.verbose):
        d.verbose = True
        
    if(opts.debug):
        d.verbose = True
        d.debug = True
        
        
#If we are running this as the main module, run the main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Closing..."