'''
This file contains functions used to parse the command line arguments
'''
import argparse
import sys
import Properties
def parseArgs(): 
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument('--port', action = 'store',dest = 'serverPort',type = int,default = 12345,help = "Port number to be used by the server")
        parser.add_argument('--without-gui', action = 'store_true' , dest = 'xServerDisabled', default = False, help = "Turns on the text only mode")
        parser.add_argument('--enable-breakpoint', action = 'store_true' , dest = 'breakPointEnabled', default = False, help = "Pauses for user input after receiving every single packet")

        results = parser.parse_args()
        if results.serverPort:
            Properties.serverPort = int(results.serverPort)

        if results.xServerDisabled:
            Properties.xServerEnabled = False
        else:
            Properties.xServerEnabled = True
        if results.breakPointEnabled:
            Properties.breakPointEnabled = True
        else:
            Properties.breakPointEnabled = False

        if Properties.serverPort < 1024 or Properties.serverPort > 65355:
            raise ValueError("port No should be a value between 1024 to 65355")
    except ValueError as e:
        printstr(str(e))
        sys.exit(1)
    except IOError, msg:
        parser.error(str(msg))
        sys.exit(1)
if __name__ == "__main__":
        #Use only for debugging
        parseArgs()