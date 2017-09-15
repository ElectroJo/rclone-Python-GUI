import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser
import getpass
from tkinter.filedialog import askopenfilename
import win32api
from tkinter import messagebox

GUI = tkinter.Tk()
ConfigButtons = []
processlist = []
rcloneCommands = ['sync','ls','delete','mount','purge','lsd']
currentcommand = tkinter.StringVar()
currentcommandlist = []
currentcommand.set("")
SourceType = ""
DestType = ""
AllLetters = ['A:', 'B:', 'C:', 'D:', 'E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'S:', 'T:', 'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:']




#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI, *Commands):
        ComputerDrives = win32api.GetLogicalDriveStrings()
        ComputerDrives = ComputerDrives.split('\\\x00')[:-1]
        if ("mount" in Commands and Commands[2] in ComputerDrives):
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


def RemoveGUI():
    for process in processlist:
        process.terminate()
    GUI.destroy()


def LoadConfigFromUser(ConFigButtonsFrame, Where="", Text = ""):
    Columnx = 0
    Rowy = 1
    global ConfigButtons
    User = getpass.getuser()
    for section in ConfigButtons:
        section.destroy()
    ConfigLable = tkinter.Label(ConFigButtonsFrame, text = Text, width = 16)
    ConfigLable.grid()
    ConfigButtons = []
    ConfigButtons.append(ConfigLable)
    ListVerYes = []
    if Text in ("Default Source:", "Default Target:", "Custom Source:", "Custom Target:"):
        Config = configparser.ConfigParser()
        if Where == "":
            Config.read("C:\\Users\\" + User +"\\.config\\rclone\\rclone.conf")
        else:
            Config.read(Where)
        ListVerYes = Config.sections()
    elif Text == "Command:":
        ListVerYes = rcloneCommands
    elif Text in ("Drive Source:", "Drive Target:"):
        if Text == "Drive Target:":
#            ListVerYes = [x for x in AllLetters if x not in ComputerDrives]
            ListVerYes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        elif Text == "Drive Source:":
            ComputerDrives = win32api.GetLogicalDriveStrings()
            ComputerDrives = ComputerDrives.split('\\\x00')[:-1]
            ComputerDrives = [x.strip(":") for x in ComputerDrives]
            ListVerYes = ComputerDrives
    for sections in ListVerYes:
        if Text in ("Default Source:", "Custom Source:", "Drive Source:"):
            ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: PickCMDCMD(sections+":",1,Text))
        elif Text in ("Default Target:", "Custom Target:", "Drive Target:"):
            ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: PickCMDCMD(sections+":",2,Text))
        elif Text == "Command:":
            ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: PickCMDCMD(sections,0))
        if Columnx == 0:
            ConfigSection.grid(column=Columnx, row=Rowy)
            Columnx = 1
        else:
            ConfigSection.grid(column=Columnx, row=Rowy)
            Rowy += 1
            Columnx = 0
        ConfigButtons.append(ConfigSection)



def LoadFile():
    ConfigFile = askopenfilename()
    return ConfigFile

def PickCMDCMD(section,position,Type=""):
    while position+1 > len(currentcommandlist):
        if len(currentcommandlist) != position+1:
            currentcommandlist.append("")
    currentcommandlist[position] = section
    currentcommand.set(" ".join(currentcommandlist))
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

def ButtonsGUI():
    ButtonsFrame = tkinter.Frame(GUI)
    ButtonsFrame.grid()

    MainButtons = tkinter.Frame(ButtonsFrame)
    MainButtons.grid(sticky='w',row=0)
    TestCommand = tkinter.Button(MainButtons, text = 'Test', width = 16,command = lambda: rcloneProcess(MainButtons, *currentcommandlist))
    TestCommand.grid(column=0, row=0)
    CloseButton = tkinter.Button(MainButtons, text = "Close", width = 16, command = lambda: RemoveGUI())
    CloseButton.grid(column=1, row=0)
    PickCommands = tkinter.Button(MainButtons, text = "Pick Command", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Command:"))
    PickCommands.grid(column = 0, row = 1)

    LineCanvas1 = tkinter.Canvas(ButtonsFrame, height = 1, width = 240)
    LineCanvas1.grid(sticky='we',row=1)
    LineCanvas1.create_line(0,0,250,0,fill='black', width=6)

    CommandButtons = tkinter.Frame(ButtonsFrame)
    CommandButtons.grid(row=2)
    SourceLable = tkinter.Label(CommandButtons, text = "Target", width = 16)
    SourceLable.grid(column = 1, row = 0)
    TargetLable = tkinter.Label(CommandButtons, text = "Source", width = 16)
    TargetLable.grid(column = 0, row = 0)
    LoadConfig = tkinter.Button(CommandButtons, text = "From Default Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Default Source:"))
    LoadConfig.grid(column = 0, row = 1)
    LoadConfigDest = tkinter.Button(CommandButtons, text = "From Default Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Default Target:"))
    LoadConfigDest.grid(column = 1, row = 1)
    LoadCustomConfig = tkinter.Button(CommandButtons, text = "From Custom Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, LoadFile(), "Custom Source:"))
    LoadCustomConfig.grid(column = 0, row = 2)
    LoadCustomConfigDest = tkinter.Button(CommandButtons, text = "From Custom Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, LoadFile(),"Custom Target:"))
    LoadCustomConfigDest.grid(column = 1, row = 2)
    PickLocalSource = tkinter.Button(CommandButtons, text = "Local Drive", width = 16,command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Source:"))
    PickLocalSource.grid(column = 0, row = 3)
    PickLocalTarget = tkinter.Button(CommandButtons, text = "Local Drive", width = 16,command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Target:"))
    PickLocalTarget.grid(column = 1, row = 3)

    CurrentCommand = tkinter.Frame(ButtonsFrame)
    CurrentCommand.grid(sticky='we',row=3)
    currentcommandlable = tkinter.Label(CurrentCommand, textvariable = currentcommand)
    currentcommandlable.grid(sticky='we')

    LineCanvas2 = tkinter.Canvas(ButtonsFrame, height = 1, width = 240)
    LineCanvas2.grid(sticky='we',row=4)
    LineCanvas2.create_line(0,0,250,0,fill='black', width=6)

    ConFigButtonsFrame = tkinter.Frame(GUI)
    ConFigButtonsFrame.grid(row=5)

def MainWindow():
    ButtonsGUI()
    tkinter.mainloop()

MainWindow()