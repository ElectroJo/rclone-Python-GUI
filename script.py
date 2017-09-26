import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser
import getpass
from tkinter.filedialog import askopenfilename
import win32api
from tkinter import messagebox
from tkinter.ttk import *


parascmd = eval(open("rcloneCommandParas.txt").read())
cmddesc = eval(open("CommandDescriptions.txt").read())
parasdesc = eval(open("ParamiterDescriptions.txt").read())
GUI = tkinter.Tk()
processlist = []
SourceType = ""
DestType = ""
AllLetters = ['A:', 'B:', 'C:', 'D:', 'E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'S:', 'T:', 'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:']




#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI, *Commands):
        ComputerDrives = win32api.GetLogicalDriveStrings()
        ComputerDrives = ComputerDrives.split('\\\x00')[:-1]
        if ("mount" in Commands and Commands[1] in ComputerDrives):
            messagebox.showerror("Error","You are trying to mount to a drive that allready exists. \nPlease pick a diffrent letter.")
        elif ("sync" in Commands and Commands[2] not in ComputerDrives and Commands[2] in AllLetters):
            messagebox.showerror("Error","You are trying to sync to a drive that doesn't exists. \nPlease pick a diffrent letter.")
        else:
            self.CommandLists = []
            self.CommandLists.append(r"rclone\rclone-v1.37-windows-amd64\rclone.exe")
            for args in Commands:
                self.CommandLists.append(args)
            self.GUI = GUI
            self.process = Popen(self.CommandLists, stdout=PIPE, stderr=STDOUT)
            global processlist
            processlist.append(self.process)
            t = Thread(target=self.reader_thread, args=[]).start()
            self.EndButton = tkinter.Button(GUI, text="Stop subprocess")
            self.EndButton = tkinter.Button(GUI, text="Stop subprocess", command = lambda: self.stop(self.EndButton))
            self.EndButton.grid()
            self.ConsoleGUIWin = tkinter.Toplevel()
            self.ConsoleGUIWin.title("Console")
            self.ConsoleFrame = tkinter.Frame(self.ConsoleGUIWin, width=900, height=500)
            self.ConsoleFrame.pack(fill="both", expand=True)
            self.ConsoleFrame.grid_propagate(False)
            self.Console = tkinter.Text(self.ConsoleFrame, width=110, height=31)
            self.Console.grid(row=1)
            self.ScrollBar = tkinter.Scrollbar(self.ConsoleFrame, command=self.Console.yview)
            self.ScrollBar.grid(row=1, column=1, sticky='ns')
        self.Console.insert(tkinter.END, str(self.CommandLists)+"\n")

    def reader_thread(self):
        for line in iter(self.process.stdout.readline, b''):
            try:
                self.Console.insert(tkinter.END, line)
            except:
                pass
            try:
                self.Console.see(tkinter.END)
            except:
                pass

    def stop(self,ende):
        self.process.terminate()
        def kill_after(countdown):
            if self.process.poll() is None:
                countdown -= 1
                if countdown < 0:
                    self.process.kill()
                else:
                    self.GUI.after(1000, kill_after, countdown)
                    return
            self.process.stdout.close()
            self.process.wait()
            ende.destroy()
        kill_after(countdown=5)

class CreateToolTip(object):
    """
    Code edited from crxguy52's response on https://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tkinter.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class TabInit:
    def __init__(self,tabs,text,command):
        self.tabs = tabs
        self.textss = text
        self.commandss = command
        self.currentcommand = tkinter.StringVar()
        self.currentcommandlist = []
        self.currentcommand.set("")
        self.ConfigButtons = []
        self.MountTab = tkinter.Frame(self.tabs)
        self.tabs.add(self.MountTab, text = self.textss)
        self.AddButtonToTab(self.MountTab,self.commandss)


    def LoadConfigFromUser(self,ConFigButtonsFrame, Where="", Text = ""):
        self.ComputerDrives = win32api.GetLogicalDriveStrings()
        self.ComputerDrives = self.ComputerDrives.split('\\\x00')[:-1]
        self.Columnx = 0
        self.Rowy = 1
        self.ConfigButtons
        self.User = getpass.getuser()
        for section in self.ConfigButtons:
            section.destroy()
        self.ConfigLable = tkinter.Label(ConFigButtonsFrame, text = Text, width = 16)
        self.ConfigLable.grid()
        self.ConfigButtons = []
        self.ConfigButtons.append(self.ConfigLable)
        self.ListVerYes = []
        if Text in ("Default Source:", "Default Target:", "Custom Source:", "Custom Target:"):
            self.Config = configparser.ConfigParser()
            if Where == "":
                self.Config.read("C:\\Users\\" + self.User +"\\.config\\rclone\\rclone.conf")
            else:
                self.Config.read(Where)
            self.ListVerYes = self.Config.sections()
        elif Text == "Command:":
            self.ListVerYes = parascmd
        elif Text in ("Drive Source:", "Drive Target:"):
            if Text == "Drive Target:":
                if self.textss == "mount":
                    self.ListVerYes = [x for x in AllLetters if x not in self.ComputerDrives]
                elif self.textss in ("sync", "ls"):
                    self.ListVerYes = [x for x in AllLetters if x in self.ComputerDrives]
                else:
                    self.ListVerYes = AllLetters
                self.ListVerYes = [x.strip(":") for x in self.ListVerYes]

            elif Text == "Drive Source:":
                self.ComputerDrives = [x.strip(":") for x in self.ComputerDrives]
                self.ListVerYes = self.ComputerDrives
        for sections in self.ListVerYes:
            if Text in ("Default Source:", "Custom Source:", "Drive Source:"):
                self.ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: self.PickCMDCMD(sections+":",1,Text))
            elif Text in ("Default Target:", "Custom Target:", "Drive Target:"):
                self.ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: self.PickCMDCMD(sections+":",2,Text))
            if self.Columnx == 0:
                self.ConfigSection.grid(column=self.Columnx, row=self.Rowy)
                self.Columnx = 1
            else:
                self.ConfigSection.grid(column=self.Columnx, row=self.Rowy)
                self.Rowy += 1
                self.Columnx = 0
            self.ConfigButtons.append(self.ConfigSection)

    def LoadFile(self):
        self.ConfigFile = askopenfilename()
        return self.ConfigFile

    def PickCMDCMD(self,section,position,Type=""):
        while position+1 > len(self.currentcommandlist):
            if len(self.currentcommandlist) != position+1:
                self.currentcommandlist.append("")
        self.currentcommandlist[position] = section
        self.currentcommand.set(" ".join(self.currentcommandlist))
        if Type in ("Default Source:", "Custom Source:", "Drive Source:"):
            if Type == "Drive Source:":
                SourceType = "Local"
            else:
                SourceType = "Remote"
        elif Type in ("Default Target:", "Custom Target:", "Drive Target:"):
            if Type ==  "Drive Target:":
                DestType = "Local"
            else:
                DestType = "Remote"


    def RcloneRemovedo(self):
        self.currentcommandlist2 = self.currentcommandlist[:]
        self.currentcommandlist2[:] = [item for item in self.currentcommandlist2 if item != '']
        rcloneProcess(self.MainButtons, *self.currentcommandlist2)

    def CheckBoxSet(self,box,position,varr):
        if varr.get() == "":
            varr.set(box)
            self.PickCMDCMD(box,position)
        else:
            varr.set("")
            self.PickCMDCMD("",position)




    def AddButtonToTab(self,Tab,command):
        self.MainButtons = tkinter.Frame(Tab)
        self.MainButtons.grid(sticky='w',row=0)
        self.TestCommand = tkinter.Button(self.MainButtons, text = 'Test', width = 16,command = lambda: self.RcloneRemovedo())
        self.TestCommand.grid(column=0, row=0)
        self.CloseButton = tkinter.Button(self.MainButtons, text = "Close", width = 16, command = lambda: RemoveGUI())
        self.CloseButton.grid(column=1, row=0)
        self.PickCMDCMD(command,0)
        self.LineCanvas1 = tkinter.Canvas(Tab, height = 1, width = 240)
        self.LineCanvas1.grid(sticky='we',row=1)
        self.LineCanvas1.create_line(0,0,250,0,fill='black', width=6)

        self.CommandButtons = tkinter.Frame(Tab)
        self.CommandButtons.grid(row=2)



        self.SourceLable = tkinter.Label(self.CommandButtons, text = "Target", width = 16)
        self.SourceLable.grid(column = 1, row = 0)
        if self.commandss in ('lsd','size','ls'):
            pass
        else:
            self.TargetLable = tkinter.Label(self.CommandButtons, text = "Source", width = 16)
            self.TargetLable.grid(column = 0, row = 0)
            self.LoadConfig = tkinter.Button(self.CommandButtons, text = "From Default Config", width = 16, command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, "", "Default Source:"))
            self.LoadConfig.grid(column = 0, row = 1)
            self.LoadCustomConfig = tkinter.Button(self.CommandButtons, text = "From Custom Config", width = 16, command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, self.LoadFile(), "Custom Source:"))
            self.LoadCustomConfig.grid(column = 0, row = 2)
            self.PickLocalSource = tkinter.Button(self.CommandButtons, text = "Local Drive", width = 16,command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Source:"))
            self.PickLocalSource.grid(column = 0, row = 3)
        self.LoadConfigDest = tkinter.Button(self.CommandButtons, text = "From Default Config", width = 16, command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, "", "Default Target:"))
        self.LoadConfigDest.grid(column = 1, row = 1)
        self.LoadCustomConfigDest = tkinter.Button(self.CommandButtons, text = "From Custom Config", width = 16, command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, self.LoadFile(),"Custom Target:"))
        self.LoadCustomConfigDest.grid(column = 1, row = 2)
        self.PickLocalTarget = tkinter.Button(self.CommandButtons, text = "Local Drive", width = 16,command = lambda: self.LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Target:"))
        self.PickLocalTarget.grid(column = 1, row = 3)

        self.CurrentCommand = tkinter.Frame(Tab)
        self.CurrentCommand.grid(sticky='we',row=3)
        self.currentcommandlable = tkinter.Label(self.CurrentCommand, textvariable = self.currentcommand)
        self.currentcommandlable.grid(sticky='we')

        self.LineCanvas2 = tkinter.Canvas(Tab, height = 1, width = 240)
        self.LineCanvas2.grid(sticky='we',row=4)
        self.LineCanvas2.create_line(0,0,250,0,fill='black', width=6)



        ConFigButtonsFrame = tkinter.Frame(Tab)
        ConFigButtonsFrame.grid(row=5)

        self.CheckBoxes = tkinter.Frame(Tab)
        self.CheckBoxes.grid(row=6)
        for self.Paras in parascmd[self.textss]:
            index = parascmd[self.textss].index(self.Paras)
            self.VcheckV = tkinter.StringVar()
            self.VcheckV.set("")
            self.VCheck = Checkbutton(self.CheckBoxes, text=self.Paras, command= lambda Paras = self.Paras, Num = index+3: self.CheckBoxSet(Paras,Num,self.VcheckV))
            self.VCheck.grid()
            try:
                self.tabdesc = CreateToolTip(self.VCheck, parasdesc[self.Paras])
            except:
                pass

def RemoveGUI():
    for process in processlist:
        process.terminate()
    GUI.destroy()

def ButtonsGUI():
    MainCommandsLabel = tkinter.Label(GUI, text="Commands")
    MainCommandsLabel.grid()
    Tabs = Notebook(GUI)
    Tabs.grid()
    for commands in parascmd:
        TabInit(Tabs,text = commands,command = commands)



def MainWindow():
    ButtonsGUI()
    tkinter.mainloop()

MainWindow()