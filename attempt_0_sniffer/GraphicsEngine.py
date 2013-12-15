#!/usr/bin/python
import Tkinter
import peek


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
        #UNDE CONSTRUCTION DON'T MODIFY
        #edited by dixit 6-10-13
        #for i in open("meta.txt").readlines():
        #    self.listBox.insert(Tkinter.END, i)     
        #END UNDER CONSTRUCTION
        
        
        
        inspectButton = Tkinter.Button(self, text = "Inspect!", command = self.onInspectButtonClick)
        inspectButton.pack()
        
        clearButton = Tkinter.Button(self, text = "Clear!", command = self.onClearButtonClick)
        clearButton.pack()
        '''UNDER CONSTRUCTION DON'T MODIFY
           edited by dixit 6-10-13
        label = Tkinter.Label(self, textvariable=self.labelVariable, anchor="w", fg="white", bg="green")
        label.grid(column = 0, row = 1, sticky = "S")
        self.labelVariable.set("This is the status window")
        self.grid_columnconfigure(0, weight = 2)
        self.resizable(True, True)
        self.update()
        #self.geometry(self.geometry())       
        #self.entry.focus_set()
        #self.entry.selection_range(0, Tkinter.END)
        END UNDER CONSTRUCTION'''
        self.labelVariable = Tkinter.StringVar()
        self.label = Tkinter.Label(self, textvariable = self.labelVariable, anchor="w", fg = "white", bg = "green")
        self.labelVariable.set("This is the summary box")
        self.label.pack(side = "bottom", fill = "both", expand = True)
        self.grid_columnconfigure(0, weight = 2)
        self.resizable(True, True)
        #self.update()
    def addLinesToDisplayList(self, lines):
        #UNDER CONSTRUCTION 
        #dixit 6-10-13
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
        #self.labelVariable.set( self.entryVariable.get()+" (You clicked the button)" )
        #self.entry.focus_set()
        #self.entry.selection_range(0, Tkinter.END)
        self.newWindow()
        
    def onClearButtonClick(self):
        self.listBox.delete(0, last = self.listBox.size())
        self.labelVariable.set("")
        peek.hashTable = {}
    def newWindow(self):
        k = PacketInspectionWindow(None, self.hashTable, self.listBox.selection_get())
        k.title('PacketInspectionWindow')
        k.mainloop()

    def onListboxSelectionChanged(self, event):
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
            #self.textBox.insert(Tkinter.INSERT, self.displayList[self.currentSelection][0]+self.displayList[self.currentSelection][1])
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