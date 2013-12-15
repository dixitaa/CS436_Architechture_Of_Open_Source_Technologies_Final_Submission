#!/usr/bin/python
import Tkinter

class StartWindow(Tkinter.Tk):
    def __init__(self,parent):
        #constructor for the application
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        self.hashTable = {}
    def initialize(self):
        #init sequence for the startup gui window
        self.grid()
        self.listBox = Tkinter.Listbox(self)
        self.listBox.pack(side="left",fill="both", expand=True)        
        self.listBox.bind("<<ListboxSelect>>", self.onListboxSelectionChanged)

        inspectButton = Tkinter.Button(self, text = "Inspect!", command = self.onInspectButtonClick)
        inspectButton.pack()
        
        clearButton = Tkinter.Button(self, text = "Clear!", command = self.onClearButtonClick)
        clearButton.pack()
        self.labelVariable = Tkinter.StringVar()
        self.label = Tkinter.Label(self, textvariable = self.labelVariable, anchor="w", fg = "white", bg = "green")
        self.labelVariable.set("This is the summary box")
        self.label.pack(side = "bottom", fill = "both", expand = True)
        self.grid_columnconfigure(0, weight = 2)
        self.resizable(True, True)
        #self.update()
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
        key = ""
        try:
            key = self.listBox.selection_get()
        except Exception as e:
            pass # This indicates Tcl Error because of a user clicking Inspect button without a corresponding selection in the list listBox
        k = PacketInspectionWindow(None, self.hashTable, key)
        k.title('PacketInspectionWindow')
        k.mainloop()        
    def onClearButtonClick(self):
        self.listBox.delete(0, last = self.listBox.size())
        self.labelVariable.set("This is the summary box")
        self.hashTable = {}

    def onListboxSelectionChanged(self, event):
        '''
            onSelectionChanged listener for the listbox
        '''
        #print peek.hashTable
        try:
            self.labelVariable.set(self.hashTable[self.listBox.selection_get()][0])
        except KeyError:
            print self.hashTable
class PacketInspectionWindow(Tkinter.Tk):
    def __init__(self,parent, displayList, currentSelection):
        #constructor for the application
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.displayList = displayList
        self.currentSelection = currentSelection
        self.initialize()

    def initialize(self):
        #init sequence for the startup gui window
        try:
            self.grid()
            self.textBox = Tkinter.Text(self, bg = "white", yscrollcommand = True)
            self.textBox.insert(Tkinter.INSERT, str(self.displayList[self.currentSelection][0]))
            self.textBox.insert(Tkinter.INSERT, str(self.displayList[self.currentSelection][1]))
            self.textBox.pack()
            self.resizable(True, True)
            self.update()
            self.geometry(self.geometry())       
        except Exception as e:
            print e, "shanda"
            print self.displayList[self.currentSelection]
            #self.textBox.insert(Tkinter.INSERT, self.displayList[self.currentSelection][0])
            pass

if __name__ == "__main__":
    app = StartWindow(None)
    app.title('my application')
    app.mainloop()