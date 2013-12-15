#****************************************************
#                                                   *
#               HTTP PROXY                          *
#               Version: 1.0                        *
#               Author: Luu Gia Thuy                *
#                                                   *
#****************************************************

import os,sys,thread,socket
import threading
import StringIO
import gzip
import re

#********* CONSTANT VARIABLES *********             #edited by dixitaa          LOL
BACKLOG = 50            # how many pending connections queue will hold
MAX_DATA_RECV = 4096    # max number of bytes we receive at once
DEBUG = False           # set to True to see the debug msgs












#class to implement client threads
class ProxyServer(threading.Thread):
    '''
        Constructor args:
        conn: TCP connection socket
        client_addr: Address Tuple of client (host, port_port)
    '''
    def __init__(self, conn, client_addr):
        threading.Thread.__init__(self)
        self.client_addr = client_addr
        self.conn = conn
        self.verbose = True
    def run(self):
        try:
            # get the request from browser
            request = self.conn.recv(MAX_DATA_RECV)

            # parse the first line
            first_line = request.split('\n')[0]

            # get url
            url = first_line.split(' ')[1]
        except IndexError:
            pass    #Just indicates a message that doesn't have an url
        if (DEBUG):
            print first_line
            print
            print "URL:",url
            print
        
        # find the webserver and port
        http_pos = url.find("://")          # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # get the rest of url
        
        port_pos = temp.find(":")           # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:       # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        print "Connect to:", webserver, port

        try:
            # create a socket to connect to the web server
            s = None
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            s.connect((webserver, port))
            request = re.sub('(Accept\-Encoding(.*)\n){1}', "", request)
            s.send(request)         # send request to webserver

            if self.verbose == True:
                print "----------------------------------------------------------------------------------------------------"
                print request
                print "----------------------------------------------------------------------------------------------------"

            while 1:
                # receive data from web server
                data = s.recv(MAX_DATA_RECV)
                
                if (len(data) > 0):
                    # send to browser
                    self.conn.send(data)
                    if self.verbose == True:
                        try:
                            if (not "image" in data):
                                print "----------------------------------------------------------------------------------------------------"
                                print data
                                print "----------------------------------------------------------------------------------------------------"

                        except IOError:
                            pass
                        except EOFError:
                            pass            #some gzip string which isn't properly terminated
                else:
                    break
            s.close()
            self.conn.close()
        except socket.error, (value, message):
            if s:
                s.close()
            if self.conn:
                self.conn.close()
            print "Runtime Error:", message
            sys.exit(1)
        except KeyboardInterrupt:
            return
    #********** END PROXY_THREAD ***********















#**************************************
#********* MAIN PROGRAM ***************
#**************************************
def main():

    # check the length of command running
    if (len(sys.argv)<2):
        print "usage: proxy <port>"  
        return sys.stdout    

    # host and port info.
    host = ''               # blank for localhost
    port = int(sys.argv[1]) # port from argument
    
    try:
        # create a socket
	s = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # associate the socket to host and port
        s.bind((host, port))

        # listenning
        s.listen(BACKLOG)
    
    except socket.error, (value, message):
        if s:
            s.close()
        print "Could not open socket:", message
        sys.exit(1)
    except KeyboardInterrupt:
        return
    # get the connection from client
    while 1:
        try:
            conn, client_addr = s.accept()

            # create a thread to handle request
            ProxyServer(conn, client_addr).start()
        except KeyboardInterrupt:
            return
    s.close()
#************** END MAIN PROGRAM ***************




    
if __name__ == '__main__':
	try:
		main()
        	threading.currentThread().join()
	except KeyboardInterrupt:
		print "\nSuccessful Exit"
        	sys.exit()
	except RuntimeError:
		pass
