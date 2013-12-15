#!/usr/bin/python
'''
This module is responsible for managing the graphical user interface
'''
import Tkinter
import tkMessageBox
import StringIO
import gzip
import Properties
import GlobalData
import sys
import time

class StartWindow(Tkinter.Tk):
    def __init__(self,parent):
        '''
        Constructor for the main window
        '''
        Tkinter.Tk.__init__(self,parent)
        self.protocol('WM_DELETE_WINDOW', self.shutdownSequence)
        self.parent = parent
        self.initialize()
        self.hashTable = {}

    def shutdownSequence(self):
        print "Bye, Server shutdown at ", time.ctime()
        Properties.ProxyServer.server_close()
        self.destroy()
        sys.exit(0)

    def initialize(self):
        '''
        Initializes and starts up the main window
        '''
        #Start off by creating a grid layout
        self.grid()
        #The center grid containing the packets
        self.listBox = Tkinter.Listbox(self)
        self.listBox.pack(side="left",fill="both", expand=True)        
        self.listBox.bind("<<ListboxSelect>>", self.onListboxSelectionChanged)

        #The Inspect button on the top right corner
        inspectButton = Tkinter.Button(self, text = "Inspect!", command = self.onInspectButtonClick)
        inspectButton.pack()

        #The Send button on the top right corner
        self.sendButton = Tkinter.Button(self, text = "Send!", command = self.onSendButtonClick)
        self.sendButton.pack()
        
        #The Clear button on the top right corner
        clearButton = Tkinter.Button(self, text = "Clear!", command = self.onClearButtonClick)
        clearButton.pack()
        self.labelVariable = Tkinter.StringVar()
        self.label = Tkinter.Label(self, textvariable = self.labelVariable, anchor="w", fg = "white", bg = "green")
        self.labelVariable.set("This is the summary box")
        self.label.pack(side = "bottom", fill = "both", expand = True)
        self.grid_columnconfigure(0, weight = 2)
        self.resizable(True, True)
        #self.update()
    def onSendButtonClick(self):
        '''
        OnClickListener for the Send button
        '''
        try:
            if Properties.breakPointEnabled == False:
               tkMessageBox.showinfo("BreakPoint Disabled", "BreakPoints are disabled, restart the application with BreakPoints enabled")
               return
            else:
                #some stuff happens here 
                key = self.listBox.selection_get()
                tamperedData = self.hashTable[key][0] +"\r\n\r\n"+ self.hashTable[key][1]
                if GlobalData.SyncDictionary.has_key(key):
                    #send the data
                    GlobalData.SyncDictionary[key] = [1, tamperedData]
                else:
                    tkMessageBox.showinfo("Already Sent", "This request/response has already been sent")
                return
        except Tkinter.TclError:
            #just indicates that no item has yet been selected in the list box
            tkMessageBox.showinfo("Item Not Selected", "Select a packet from the list and try again!")
            pass
    def addLinesToDisplayList(self, lines):
        '''
            receives a list with the first element being the packet headers and the second being the data in the packet
        '''
        try:
            tl = lines[0].splitlines()
            index = tl[0]+"\t\t"+tl[1]+"\t\t"+tl[2]
            self.listBox.insert(Tkinter.END, index)
            self.hashTable[index] = []
            self.hashTable[index].insert(0, lines[0])
            self.hashTable[index].insert(1, lines[1])
        except IndexError:
            self.hashTable[index].insert(1, "")
            pass    #IndexErrors are let go if the packet doesn't have any data
    def onInspectButtonClick(self):
        '''
        Creates a new packet inspection window once the Inspect! button is clicked
        '''
        try:
            key = ""
            key = self.listBox.selection_get()
            k = PacketInspectionWindow(None, self.hashTable, key)
            k.title('PacketInspectionWindow')
            k.mainloop()
        except Tkinter.TclError:
            #Just indicates that no item has yet been selected in the list box
            tkMessageBox.showinfo("Item Not Selected", "Select a packet from the list and try again!")
            pass
    def onClearButtonClick(self):
        '''
        OnClickListener for the Clear button
        '''
        self.listBox.delete(0, last = self.listBox.size())
        self.labelVariable.set("This is the summary box")
        self.hashTable = {}

    def onListboxSelectionChanged(self, event):
        '''
            onSelectionChanged listener for the listbox
        '''
        try:
            self.labelVariable.set(self.hashTable[self.listBox.selection_get()][0])
        except KeyError:
            print self.hashTable
        except Tkinter.TclError:
            #Signifies that the listBox has just been cleared, so let it pass
            pass

class PacketInspectionWindow(Tkinter.Tk):
    def __init__(self, parent, displayList, currentSelection):
        '''
        Constructor for the packet inspection window
        '''
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.displayList = displayList
        self.currentSelection = currentSelection
        self.initialize()
        self.isGzipped = True
    def initialize(self):
        '''
        Initialization sequence for the startup gui window
        '''
        try:
            #Start off by creating a grid layout
            self.grid()
            self.textBox = Tkinter.Text(self, bg = "white", yscrollcommand = True)
            self.sendButton = Tkinter.Button(self, text = "Send!", command = self.onSendButtonClick)
            self.sendButton.pack()
            self.textBox.insert(Tkinter.INSERT, str(self.displayList[self.currentSelection][0])+"\r\n\r\n")
            
            gzippedString = self.displayList[self.currentSelection][1]

            #Extracting a gzipped string
            s = StringIO.StringIO(gzippedString)
            f = gzip.GzipFile(fileobj = s)
            self.textBox.insert(Tkinter.INSERT, "\n-----------------------------------------------------------------------------------------------------\nThe TEXT below this line is the data contained within the packet, remove this line and the dashes before you send out the packet!\n-----------------------------------------------------------------------------------------------------\n"+ f.read())

            self.textBox.pack()
            self.resizable(True, True)
            self.update()
            self.geometry(self.geometry())       
        except Exception as e:
            try:
                self.isGzipped = False
                l = str(self.displayList[self.currentSelection][1])
                self.textBox.insert(Tkinter.INSERT, "\n-----------------------------------------------------------------------------------------------------\nThe TEXT below this line is the data contained within the packet, remove this line and the dashes before you send out the packet!\n-----------------------------------------------------------------------------------------------------\n"+l)
                self.textBox.pack()
                self.resizable(True, True)
                self.update()
                self.geometry(self.geometry())
                #self.textBox.insert(Tkinter.INSERT, l)
            except Exception as e:
                print e
                pass    #Let a second time exception pass

    def onSendButtonClick(self):
        '''
        OnClickListener for the Send button
        '''
        if Properties.breakPointEnabled == False:
           tkMessageBox.showinfo("BreakPoint Disabled", "BreakPoints are disabled, restart the application with BreakPoints enabled")
           return
        else:
            #Extract the tampered data and send it across
            self.tamperedData = self.textBox.get(1.0, Tkinter.END)
            if GlobalData.SyncDictionary.has_key(self.currentSelection):
                    GlobalData.SyncDictionary[self.currentSelection] = [1, self.tamperedData]

            else:
                tkMessageBox.showinfo("Already Sent", "This request/response has already been sent")

            return

if __name__ == "__main__":
    '''
    This part of the code is only meant for debugging purposes
    '''
    try:
        app = StartWindow(None)
        app.title('my application')
        app.mainloop()
    except KeyboardInterrupt:
        #Close all the GUI and exit
        app.destroy()