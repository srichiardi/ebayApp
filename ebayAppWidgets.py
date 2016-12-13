import os
from Tkinter import *
import Tkinter, tkFileDialog


##-------------------------------------------------------------##
##-----------------------------GUIs----------------------------##
##-------------------------------------------------------------##

class appDlg(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title("eBay App Search")
        self.geometry("410x235")
        rootDir = os.path.split(__file__)[0]
        self.optionsDict = { 'outputFolder' : rootDir }
        
        self.frames = [{ 'label' : 'Seller ID',
                         'input' : 'entry',
                         'appOpt' : 'sellerId' },
                        { 'label' : 'Results per page',
                          'input' : 'entry',
                          'appOpt' : 'totResults' },
                        { 'label' : 'Start from page',
                          'input' : 'entry',
                          'appOpt' : 'startFromPage' },
                        { 'label' : 'Sold items only',
                          'input' : 'option',
                          'appOpt' : 'soldOnly' },
                        { 'label' : 'Keywords',
                          'input' : 'entry',
                          'appOpt' : 'keywords' },
                        { 'label' : 'Save to: ',
                          'input' : 'browse',
                          'appOpt' : 'outputPath' }
                        ]

        for level in self.frames:
            frame = Frame(self)
            frame.pack(pady=5,side=TOP,fill=X)
            label = Label(frame,text=level['label'])
            if level['input'] == 'entry':
                wdgt = Entry(frame,width=50)
            elif level['input'] == 'option':
                var = IntVar()
                wdgt = Checkbutton(frame, variable=var)
                level['var'] = var
            elif level['input'] == 'browse':
                wdgt = Button(frame, text="Browse", command=self.outputDir)
            wdgt.pack(side=RIGHT,padx=5)
            label.pack(side=RIGHT,padx=5)
            level['wdgt'] = wdgt

        self.bottomFrame = Frame(self)
        self.bottomFrame.pack(pady=5,side=TOP,fill=X)
        self.btnRun = Button(self.bottomFrame, text="Run", command=self.close)
        self.btnRun.pack(side=RIGHT,padx=5)
        

    def outputDir(self):
        self.optionsDict['outputFolder'] = tkFileDialog.askdirectory()

    
    def close(self):
        for level in self.frames:
            if level['input'] == 'entry':
                self.optionsDict[level['appOpt']] = level['wdgt'].get()
            elif level['input'] == 'option':
                if level['var'].get() == 1:
                    self.optionsDict[level['appOpt']] = True
                else:
                    self.optionsDict[level['appOpt']] = False
        self.destroy()


    def mainloop(self):
        Tk.mainloop(self)
        return self.optionsDict
