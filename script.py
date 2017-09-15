import subprocess
from subprocess import Popen, PIPE, STDOUT
import tkinter
from threading import Thread
import configparser
import getpass
from tkinter.filedialog import askopenfilename
import win32api

GUI = tkinter.Tk()
ConfigButtons = []
processlist = []
rcloneCommands = ['sync','ls','delete','mount','purge','lsd']
currentcommand = tkinter.StringVar()
currentcommandlist = []
currentcommand.set("")




#Some code from: https://gist.github.com/zed/42324397516310c86288
class rcloneProcess:
    def __init__(self, GUI, *Commands):
        print()
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
        self.process.terminate() # tell the subprocess to exit

        # kill subprocess if it hasn't exited after a countdown
        def kill_after(countdown):
            if self.process.poll() is None: # subprocess hasn't exited yet
                countdown -= 1
                if countdown < 0: # do kill
                    self.process.kill() # more likely to kill on *nix
                else:
                    self.GUI.after(1000, kill_after, countdown)
                    return # continue countdown in a second
            # clean up
            self.process.stdout.close()  # close fd
            self.process.wait()
            ende.destroy()       # wait for the subprocess' exit
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
        ComputerDrives = win32api.GetLogicalDriveStrings()
        ComputerDrives = ComputerDrives.split('\\\x00')[:-1]
        ComputerDrives = [x.strip(":") for x in ComputerDrives]
        if Text == "Drive Target:":
            AllLetters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            ListVerYes = [x for x in AllLetters if x not in ComputerDrives]
        elif Text == "Drive Source:":
            ListVerYes = ComputerDrives
    for sections in ListVerYes:
        if Text in ("Default Source:", "Custom Source:", "Drive Source:"):
            ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: PickCMDCMD(sections+":",1))
        elif Text in ("Default Target:", "Custom Target:", "Drive Target:"):
            ConfigSection = tkinter.Button(ConFigButtonsFrame, width = 16, text = sections, command = lambda sections=sections: PickCMDCMD(sections+":",2))
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

def PickCMDCMD(section,position):
    while position+1 > len(currentcommandlist):
        if len(currentcommandlist) != position+1:
            currentcommandlist.append("")
    currentcommandlist[position] = section
    currentcommand.set(" ".join(currentcommandlist))

def ButtonsGUI():
    ButtonsFrame = tkinter.Frame(GUI)
    ButtonsFrame.grid()

    MainButtons = tkinter.Frame(ButtonsFrame)
    MainButtons.grid(sticky='w')

    CurrentCommand = tkinter.Frame(ButtonsFrame)
    CurrentCommand.grid(sticky='we')

    LineCanvas = tkinter.Canvas(ButtonsFrame, height = 1, width = 240)
    LineCanvas.grid(sticky='we')

    ConFigButtonsFrame = tkinter.Frame(GUI)
    ConFigButtonsFrame.grid()


    currentcommandlable = tkinter.Label(CurrentCommand, textvariable = currentcommand)
    currentcommandlable.grid(sticky='we')
    TestCommand = tkinter.Button(MainButtons, text = 'Test', width = 16,command = lambda: rcloneProcess(MainButtons, *currentcommandlist))
    TestCommand.grid(row=0,column=0)
    CloseButton = tkinter.Button(MainButtons, text = "Close", width = 16, command = lambda: RemoveGUI())
    CloseButton.grid(row=0,column=1)
    LoadConfig = tkinter.Button(MainButtons, text = "From Default Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Default Source:"))
    LoadConfig.grid(column = 0, row = 3)
    LoadConfigDest = tkinter.Button(MainButtons, text = "From Default Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Default Target:"))
    LoadConfigDest.grid(column = 1, row = 3)
    PickCommands = tkinter.Button(MainButtons, text = "Pick Command", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Command:"))
    PickCommands.grid(column = 0, row = 1)
    LoadCustomConfig = tkinter.Button(MainButtons, text = "From Custom Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, LoadFile(), "Custom Source:"))
    LoadCustomConfig.grid(column = 0, row = 4)
    LoadCustomConfigDest = tkinter.Button(MainButtons, text = "From Custom Config", width = 16, command = lambda: LoadConfigFromUser(ConFigButtonsFrame, LoadFile(),"Custom Target:"))
    LoadCustomConfigDest.grid(column = 1, row = 4)
    PickLocalSource = tkinter.Button(MainButtons, text = "Local Drive", width = 16,command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Source:"))
    PickLocalSource.grid(column = 0, row = 5)
    PickLocalTarget = tkinter.Button(MainButtons, text = "Local Drive", width = 16,command = lambda: LoadConfigFromUser(ConFigButtonsFrame, "", "Drive Target:"))
    PickLocalTarget.grid(column = 1, row = 5)
    SourceLable = tkinter.Label(MainButtons, text = "Target", width = 16)
    SourceLable.grid(column = 1, row = 2)
    TargetLable = tkinter.Label(MainButtons, text = "Source", width = 16)
    TargetLable.grid(column = 0, row = 2)
    LineCanvas.create_line(0,0,250,0,fill='black', width=6)

def MainWindow():
    ButtonsGUI()
    tkinter.mainloop()

MainWindow()