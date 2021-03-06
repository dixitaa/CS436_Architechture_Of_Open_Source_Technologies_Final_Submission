#!/usr/bin/python

import Properties
from GraphicsEngine import *
from ArgumentParser import *
from GlobalData import *

from sys import argv

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

from urlparse import urlparse
from urlparse import urlunparse
from urlparse import ParseResult
from httplib import HTTPResponse
from tempfile import gettempdir

from os import path
from os import listdir
from ssl import wrap_socket
from ssl import SSLError
from socket import socket
from threading import Thread

from OpenSSL.crypto import (X509Extension, X509, dump_privatekey, dump_certificate, load_certificate, load_privatekey, PKey, TYPE_RSA, X509Req)
from OpenSSL.SSL import FILETYPE_PEM

import select



class UnsupportedSchemeException(Exception):
    pass


class ProxyHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.is_connect = False
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def _connect_to_host(self):
        '''
        Establishes an ssl tunnel if it is a https request
        '''
        # Get hostname and port to connect to
        if self.is_connect:
            self.hostname, self.port = self.path.split(':')
        else:
            u = urlparse(self.path)
            if u.scheme != 'http':
                raise UnsupportedSchemeException('Unknown scheme %s' % repr(u.scheme))
            self.hostname = u.hostname
            self.port = u.port or 80
            self.path = urlunparse(
                ParseResult(
                    scheme='',
                    netloc='',
                    params=u.params,
                    path=u.path or '/',
                    query=u.query,
                    fragment=u.fragment
                )
            )

        # Connect to destination
        self._proxy_sock = socket()
        self._proxy_sock.settimeout(10)
        self._proxy_sock.connect((self.hostname, int(self.port)))

        # Wrap socket if SSL is required
        if self.is_connect:
            self._proxy_sock = wrap_socket(self._proxy_sock)


    def _transition_to_ssl(self):
        '''
        Transforms the existing non-ssl connection socket to an ssl socket
        '''
        self.request = wrap_socket(self.request, server_side = True, certfile = self.server.ca[self.path.split(':')[0]])


    def do_CONNECT(self):
        '''
        The default call back method for the http CONNECT method, which is used for establishing a tunnel between the proxy server and the host
        '''
        self.is_connect = True
        try:
            # Connect to destination first
            self._connect_to_host()

            # If successful, let's do this!
            self.send_response(200, 'Connection established')
            self.end_headers()
            #self.request.sendall('%s 200 Connection established\r\n\r\n' % self.request_version)
            self._transition_to_ssl()
        except Exception, e:
            self.send_error(500, str(e))
            return

        # Reload!
        try:
            self.setup()
            self.ssl_host = 'https://%s' % self.path
            self.handle_one_request()
        except SSLError:
            pass    #Indicates an exception reaised due to an unknow certificate authority  

    def do_COMMAND(self):
        '''
        This is yet to be filled
        '''

        # Is this an SSL tunnel?
        if not self.is_connect:
            try:
                # Connect to destination
                self._connect_to_host()
            except Exception, e:
                self.send_error(500, str(e))
                return
            # Extract path

        # Build request
        req = '%s %s %s\r\n' % (self.command, self.path, self.request_version)

        # Add headers to the request
        req += '%s\r\n' % self.headers

        # Append message body if present to the request
        if 'Content-Length' in self.headers:
            req += self.rfile.read(int(self.headers['Content-Length']))

        # Send it down the pipe!
        self._proxy_sock.sendall(self.mitm_request(req))

        # Parse response
        h = HTTPResponse(self._proxy_sock)
        h.begin()

        # Get rid of the pesky header
        del h.msg['Transfer-Encoding']

        #  Time to relay the message across
        res = '%s %s %s\r\n' % (self.request_version, h.status, h.reason)
        res += '%s\r\n' % h.msg
        res += h.read()

        # Let's close off the remote end
        h.close()
        self._proxy_sock.close()

        # Relay the message
        self.request.sendall(self.mitm_response(res))

    def mitm_request(self, data):
        for p in self.server._req_plugins:
            data = p(self.server, self).do_request(data)
        return data

    def mitm_response(self, data):
        for p in self.server._res_plugins:
            data = p(self.server, self).do_response(data)
        return data

    def __getattr__(self, item):
        if item.startswith('do_'):
            return self.do_COMMAND

    def log_message(self, format, *args):
        '''
            Disables the automatic logging enabled by BaseHTTPServer
        '''
        return


class InterceptorPlugin(object):
    '''
    The Skeleton class for Interceptor plugins, they just receive the data passing through them
    '''
    def __init__(self, server, message):
        self.server = server
        self.message = message



class CertificateAuthority(object):

    def __init__(self, ca_file='ca.pem', cache_dir=gettempdir()):
        '''
        The constructor for making a certificate authority file
        '''
        self.ca_file = ca_file
        self.cache_dir = cache_dir
        self._serial = self._get_serial()
        if not path.exists(ca_file):
            self._generate_ca()
        else:
            self.readCertificateAuthorityFile(ca_file)

    def _get_serial(self):
        '''
        Makes sure that every certificate is associated with an unique serial number
        '''
        s = 1
        for c in filter(lambda x: x.startswith('.pymp_'), listdir(self.cache_dir)):
            c = load_certificate(FILETYPE_PEM, open(path.sep.join([self.cache_dir, c])).read())
            sc = c.get_serial_number()
            if sc > s:
                s = sc
            del c
        return s

    def _generate_ca(self):
        '''
        This function generates the certificate authority file
        '''
        # Generate key
        self.key = PKey()
        self.key.generate_key(TYPE_RSA, 2048)

        # Generate certificate
        self.cert = X509()
        self.cert.set_version(3)
        self.cert.set_serial_number(1)
        self.cert.get_subject().CN = 'ca.mitm.com'
        self.cert.gmtime_adj_notBefore(0)
        self.cert.gmtime_adj_notAfter(315360000)
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.add_extensions([
            X509Extension("basicConstraints", True, "CA:TRUE, pathlen:0"),
            X509Extension("keyUsage", True, "keyCertSign, cRLSign"),
            X509Extension("subjectKeyIdentifier", False, "hash", subject=self.cert),
            ])
        self.cert.sign(self.key, "sha1")

        with open(self.ca_file, 'wb+') as f:
            f.write(dump_privatekey(FILETYPE_PEM, self.key))
            f.write(dump_certificate(FILETYPE_PEM, self.cert))

    def readCertificateAuthorityFile(self, file):
        '''
        Reads a CA file assuming it is already present and configured
        '''
        self.cert = load_certificate(FILETYPE_PEM, open(file).read())
        self.key = load_privatekey(FILETYPE_PEM, open(file).read())

    def __getitem__(self, cn):
        '''
        Gets the specified Certificate authority file if it already exists, else creates one!
        '''
        cnp = path.sep.join([self.cache_dir, '.pymp_%s.pem' % cn])
        if not path.exists(cnp):
            # create certificate
            key = PKey()
            key.generate_key(TYPE_RSA, 2048)

            # Generate CSR
            req = X509Req()
            req.get_subject().CN = cn
            req.set_pubkey(key)
            req.sign(key, 'sha1')

            # Sign CSR
            cert = X509()
            cert.set_subject(req.get_subject())
            cert.set_serial_number(self.serial)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(31536000)
            cert.set_issuer(self.cert.get_subject())
            cert.set_pubkey(req.get_pubkey())
            cert.sign(self.key, 'sha1')

            with open(cnp, 'wb+') as f:
                f.write(dump_privatekey(FILETYPE_PEM, key))
                f.write(dump_certificate(FILETYPE_PEM, cert))

        return cnp

    @property
    def serial(self):
        '''
        A static function which generates a unique serial number for every certificate
        '''
        self._serial += 1
        return self._serial






class RequestInterceptorPlugin(InterceptorPlugin):
    '''
    Interceptor plugin class for requests
    '''
    def do_request(self, data):
        return data


class ResponseInterceptorPlugin(InterceptorPlugin):
    '''
    Interceptor plugin class for responses
    '''
    def do_response(self, data):
        return data


class InvalidInterceptorPluginException(Exception):
    '''
    Exception class for Plugins which aren't subclassed from the InterceptorPlugin class
    '''
    pass


class BaseKProxy(HTTPServer):
    '''
    The class which implements tha proxy server
    '''
    def __init__(self, server_address=('', 8900), RequestHandlerClass = ProxyHandler, bind_and_activate=True, ca_file='ca.pem'):
        HTTPServer.__init__(self, ('', Properties.serverPort), RequestHandlerClass, bind_and_activate)
        self.ca = CertificateAuthority(ca_file)
        self._res_plugins = []
        self._req_plugins = []  

    def register_interceptor(self, interceptor_class):
        '''
        Registers Interceptors for the proxy servers
        '''
        if not issubclass(interceptor_class, InterceptorPlugin):
            raise InvalidInterceptorPluginException('Expected type InterceptorPlugin got %s instead' % type(interceptor_class))
        if issubclass(interceptor_class, RequestInterceptorPlugin):
            self._req_plugins.append(interceptor_class)
        if issubclass(interceptor_class, ResponseInterceptorPlugin):
            self._res_plugins.append(interceptor_class)


class AsynchronousKProxy(ThreadingMixIn, BaseKProxy):
    '''
    Ultimately subclassed from BaseHTTPServer, responsible for making sure that multiple threads are spawned for multiple requests
    '''
    pass

class DebugInterceptor(RequestInterceptorPlugin, ResponseInterceptorPlugin):

        def do_request(self, data):
            '''
            This method is responsible for logging and managing the user interface for responses recieved
            '''
            #print '>> %s' % repr(data)
            key = ""
            try:
                if Properties.xServerEnabled:
                    headers = data
                    d = ""
                    headers, d = data.split("\r\n\r\n")
                    localList = headers.splitlines()
                    key = localList[0] +"\t\t"+ localList[1] +"\t\t"+ localList[2]
            except IndexError:
                pass
            if Properties.xServerEnabled:
                Properties.GUIManager.addLinesToDisplayList([headers, d])
            else:
                print "\n------------------------------------------\n"+data+"\n------------------------------------------\n"
            if Properties.breakPointEnabled == False:
                return data
            else:
                try:    
                    #Implies that a break-point has been set, add an element to the synchronizing dictionary
                    GlobalData.SyncDictionary[key] = [0, ""]     #indicates a list of tampered data, 0 stands for don't send and "" stands for the tampered data to be sent
                    while GlobalData.SyncDictionary[key] == [0, ""]:
                        continue    #wait until the data is tampered with
                    #send out the tampered data
                    tamperedData = GlobalData.SyncDictionary[key][1]
                    GlobalData.SyncDictionary.pop(key)
                    return tamperedData
                except keyError:
                    #KeyError implies that the SyncDicionary doesn't have the indicated key implying that the listBox in the GUI has been cleared and the breakpoint needs to stop
                    pass
        def do_response(self, data):
            '''
            This method is responsible for logging and managing the user interface for responses recieved
            '''
            #print '<< %s' % repr(data)
            key = ""
            try:
                if Properties.xServerEnabled:
                    headers = data
                    d = ""
                    headers, d = data.split("\r\n\r\n")
                    localList = headers.splitlines()
                    key = localList[0] +"\t\t"+ localList[1] +"\t\t"+ localList[2]
            except IndexError:
                pass
            except ValueError:
                #Just indicates that there are too many values to split, ie:no GlobalData
                pass
            if Properties.xServerEnabled:
                Properties.GUIManager.addLinesToDisplayList([headers, d])
            else:
                print "\n------------------------------------------\n"+data+"\n------------------------------------------\n" 
            if Properties.breakPointEnabled == False:
                return data

            else:
                try:
                    #Implies that a break-point has been set, add an element to the synchronizing dictionary
                    GlobalData.SyncDictionary[key] = [0, ""]     #indicates a list of tampered data, 0 stands for don't send and "" stands for the tampered data to be sent
                    while GlobalData.SyncDictionary[key] == [0, ""]:    
                        continue    #wait until the data is tampered with
                    #send out the tampered data
                    tamperedData = GlobalData.SyncDictionary[key][1]
                    GlobalData.SyncDictionary.pop(key)
                    return tamperedData
                except keyError:
                    #KeyError implies that the SyncDicionary doesn't have the indicated key implying that the listBox in the GUI has been cleared and the breakpoint needs to stop
                    pass 
class ProxyThread(Thread):
    '''
    This class is responsible for spawning the Proxy Server
    '''
    def __init__(self):
        Thread.__init__(self)
        self.proxy = AsynchronousKProxy(ca_file = "ca.pem")
        self.proxy.register_interceptor(DebugInterceptor)
        Properties.ProxyServer = self.proxy
    def run(self):
        try:
            self.proxy.serve_forever()
        except select.error:
            #Indicates server shutdown due closing the window
            pass
if __name__ == '__main__':

    #Parse all the command line arguments
    parseArgs()

    ProxyThread().start()
    if Properties.xServerEnabled == True:
        GlobalData.SyncDictionary = {}
        Properties.GUIManager = StartWindow(None)
        Properties.GUIManager.title("K-proxy")
        Properties.GUIManager.mainloop()