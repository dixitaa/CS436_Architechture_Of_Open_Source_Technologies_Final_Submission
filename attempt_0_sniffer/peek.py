import pcapy
import sys
import gzip
import StringIO
import threading
from impacket.ImpactDecoder import *
import GraphicsEngine


class PacketCapturer():
    listOfInterfaces = []
    currentInterface = ""
    readTimeout = 100
    maxBytes = 4096
    HTTPHeaders = ""

    promiscuousMode = True

    def __init__(self, GUIManager):
        self.listOfInterfaces = pcapy.findalldevs()
        self.GUIManager = GUIManager
        self.packetList = []    #contains the list of all the packets captured
    def openInterface(self, interface):
        #UNDER CONSTRUCTION 
        #MODIFIED BY DIXIT 6-10-13
        self.currentInterface = interface
        self.interfaceHandler = pcapy.open_live(self.currentInterface, self.maxBytes, self.promiscuousMode, self.readTimeout)
        
        
    def startCapture(self):
        self.interfaceHandler.setfilter('tcp')
        self.interfaceHandler.loop(-1, self.onPacketReceived)    # -1 signifies receive infinitely    
   
        

    def onPacketReceived(self, headers, data):
        #ONGOING CONSTRUCION
        packet =  EthDecoder().decode(data)       
        try:
            HTTPPacket = packet.child().child()
            tempList = HTTPPacket.get_data_as_string().split("\r\n\r\n")
            localList = []  #just another local list
            HTTPHeaders = tempList[0]
            if tempList == [''] or tempList == []:
                return

            if HTTPHeaders != "" and ("http" in HTTPHeaders.lower()):    #to capture only the HTTP or HTTPs TRAFFIC
                localList.insert(0, HTTPHeaders)
            else:
                return    
            gzippedString = tempList[1]
            if gzippedString != "" and gzippedString != "0":
                s = StringIO.StringIO(gzippedString)
                f = gzip.GzipFile(fileobj=s)
                localList.insert(1, f.read())
                #print "HTTP DATA:\n----------"
                #self.GUIManager.addLinesTolistBox("This is the data part\n-----------------------------".splitlines())
                #self.GUIManager.addLinesToListBox(f.readlines())
                f.close()
            self.GUIManager.addLinesToDisplayList(localList)
        except IndexError as e:
            pass    #Just indicates a dummy packet
        except Exception as e:
            #print e
            #self.GUIManager.addLinesToDisplayList(localList)
            pass
        
        
        
        
        
        
    #getter and setter methods after this line
    def getCurrentInterface(self):
        return self.currentInterface
    def getListOfInterfaces(self):
        #returns a list of available interfaces 
        return self.listOfInterfaces
    def getReadTimeout(self):
        return self.readTimeout
    def getMaxBytes(self):
        return self.maxBytes
    def getPromiscuousMode(self):
        return self.promiscuousMode
    def setCurrentInterface(self, newInterface):
        #changes the interface on which the packets are being captured
        #TO BE MODIFIED, MAY CONTAIN LOGICAL ERRORS
        if newInterface in self.listOfInterfaces:
            self.currentInterface = newInterface
        else:
            raise Exception("Invalid interface to capture from")
    def setReadTimeout(self, newReadTimeout):
        if type(newReadTimeout) == "int":
            self.readTimeout = newReadTimeout
        '''else:
            raise Exception("Invalid readTimeout value specified")
        '''
    def setMaxBytes(self, newMaxBytes):
        if type(newMaxBytes) == "int":
            self.maxBytes = newMaxBytes
        else:
            raise Exception("Invalid maxBytes value specified")
    def setPromiscuousMode(self, newPromiscuousMode):
        if type(newPromiscuousMode) == "bool":
            self.promiscuousMode = newPromiscuousMode
        else:
            raise Exception("Invalid promiscuousMode specified")
        
    def getHTTPStatusCode(self, headerString):
        try:
            pass
        except IndexError:
            pass
        
        
#END CLASS Peek


#START CLASS UIThreadklajs
class PacketCaptureThread(threading.Thread):
    def __init__(self, GUIManager):
        threading.Thread.__init__(self)
        self.GUIManager = GUIManager
    def run(self):
        self.p = PacketCapturer(self.GUIManager)     
        print 'list of interfaces available are ', self.p.listOfInterfaces
        self.p.openInterface(self.p.listOfInterfaces[2])
        self.p.startCapture()
      

if __name__ == "__main__":
    #IT ALL STARTS HERE
    print "PEEK 1.0 DEBUGGING SHELL"
    print "peek>",
    try:
        hashTable = {}
        GUIManager = GraphicsEngine.StartWindow(None)
        GUIManager.title("PEEK 1.0 ALPHA")

        PCThread = PacketCaptureThread(GUIManager)
        PCThread.start()
        GUIManager.mainloop() 
        
        print "Does this ever get printed?"
        #p.GUIManager.mainloop()
        threading.current_thread().join()
    except Exception as e:
        print e
        print type(e)
        pass    
